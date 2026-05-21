"""
agent-splitter.py — Deterministic call-graph analysis and bottom-up annotation orchestrator.

Parses a Python source file, builds a call graph of all top-level functions and
class methods, detects strongly connected components (mutual recursion) via
Tarjan's algorithm, topological-sorts from leaf functions to root callers, then
invokes agent-writer.py once per function (or per small SCC) in that order.

This agent uses NO LLM calls — it is purely deterministic.
"""

import argparse
import ast
import json
import re
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from common import log

AGENT_NAME = "agent-splitter"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class FunctionInfo:
    """Metadata for one function or method extracted from the source file."""
    name: str                     # qualified name: "func" or "ClassName.method"
    ast_node: ast.FunctionDef
    source: str                   # raw source text of the function
    start_line: int               # 1-based line in the original file
    end_line: int                 # 1-based inclusive
    class_name: Optional[str] = None
    callees: set = field(default_factory=set)  # qualified names of called functions
    is_dunder: bool = False
    is_property: bool = False
    annotated_source: Optional[str] = None
    contracts: Optional[str] = None  # extracted #@ lines after annotation


# ---------------------------------------------------------------------------
# AST-based call-graph analysis
# ---------------------------------------------------------------------------

def _qualified_name(func_name: str, class_name: Optional[str]) -> str:
    if class_name:
        return f"{class_name}.{func_name}"
    return func_name


def _extract_functions(source: str) -> tuple[list[FunctionInfo], dict[str, FunctionInfo]]:
    """Parse source and extract all top-level functions and class methods."""
    tree = ast.parse(source)
    source_lines = source.splitlines(keepends=True)
    functions: list[FunctionInfo] = []
    func_map: dict[str, FunctionInfo] = {}

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            info = _make_func_info(node, source_lines, class_name=None)
            functions.append(info)
            func_map[info.name] = info
        elif isinstance(node, ast.ClassDef):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.FunctionDef):
                    info = _make_func_info(child, source_lines, class_name=node.name)
                    functions.append(info)
                    func_map[info.name] = info

    return functions, func_map


def _make_func_info(node: ast.FunctionDef, source_lines: list[str],
                    class_name: Optional[str]) -> FunctionInfo:
    start = node.lineno  # 1-based
    end = node.end_lineno or start
    source = "".join(source_lines[start - 1 : end])

    qname = _qualified_name(node.name, class_name)
    is_dunder = node.name.startswith("__") and node.name.endswith("__")
    is_property = any(
        isinstance(d, ast.Name) and d.id == "property"
        for d in node.decorator_list
    )

    return FunctionInfo(
        name=qname,
        ast_node=node,
        source=source,
        start_line=start,
        end_line=end,
        class_name=class_name,
        is_dunder=is_dunder,
        is_property=is_property,
    )


def _build_call_graph(functions: list[FunctionInfo],
                      func_map: dict[str, FunctionInfo]) -> None:
    """Populate each FunctionInfo.callees with the qualified names it calls."""
    all_names = set(func_map.keys())
    # Build a set of unqualified → qualified mappings for resolution
    unq_to_q: dict[str, list[str]] = {}
    for qname in all_names:
        short = qname.split(".")[-1]
        unq_to_q.setdefault(short, []).append(qname)

    for info in functions:
        for node in ast.walk(info.ast_node):
            if not isinstance(node, ast.Call):
                continue

            callee_name = None

            # Direct call: func(...)
            if isinstance(node.func, ast.Name):
                callee_name = node.func.id
            # Method call on self: self.method(...)
            elif (isinstance(node.func, ast.Attribute)
                  and isinstance(node.func.value, ast.Name)
                  and node.func.value.id == "self"
                  and info.class_name):
                callee_name = node.func.attr

            if callee_name is None:
                continue

            # Resolve to qualified names
            # First try exact match within same class for methods
            if info.class_name:
                same_class_q = f"{info.class_name}.{callee_name}"
                if same_class_q in all_names and same_class_q != info.name:
                    info.callees.add(same_class_q)
                    continue

            # Then try unqualified resolution
            candidates = unq_to_q.get(callee_name, [])
            for cand in candidates:
                if cand != info.name:
                    info.callees.add(cand)


# ---------------------------------------------------------------------------
# Tarjan's SCC algorithm
# ---------------------------------------------------------------------------

def _tarjan_scc(func_map: dict[str, FunctionInfo]) -> list[list[str]]:
    """Return SCCs in reverse topological order (leaves first)."""
    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    result: list[list[str]] = []

    def strongconnect(v: str):
        indices[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        info = func_map.get(v)
        successors = info.callees if info else set()

        for w in successors:
            if w not in func_map:
                continue  # external call, skip
            if w not in indices:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in on_stack:
                lowlinks[v] = min(lowlinks[v], indices[w])

        if lowlinks[v] == indices[v]:
            component = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == v:
                    break
            result.append(component)

    for v in func_map:
        if v not in indices:
            strongconnect(v)

    return result  # already in reverse topological order


# ---------------------------------------------------------------------------
# File reassembly
# ---------------------------------------------------------------------------

def _extract_contracts_text(annotated_source: str) -> str:
    """Extract just the #@ contract lines from an annotated function."""
    lines = []
    for line in annotated_source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#@"):
            lines.append(stripped)
    return "\n".join(lines)


def _extract_class_context(source: str, class_name: str) -> str:
    """Extract the class definition header, __init__, and any class invariants for context."""
    tree = ast.parse(source)
    source_lines = source.splitlines(keepends=True)

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            parts = []

            # Collect #@ class invariant lines immediately before the class def
            class_line = node.lineno - 1  # 0-based
            inv_start = class_line
            while inv_start > 0 and source_lines[inv_start - 1].strip().startswith("#@"):
                inv_start -= 1
            for idx in range(inv_start, class_line):
                stripped = source_lines[idx].strip()
                if stripped.startswith("#@"):
                    parts.append(stripped)

            parts.append(f"class {class_name}:")

            # Include __init__ body
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                    start = child.lineno - 1
                    end = child.end_lineno or child.lineno
                    init_src = "".join(source_lines[start:end])
                    parts.append(init_src)
                    break
            return "\n".join(parts)
    return ""


def _generate_class_invariants(
    source: str,
    functions: list[FunctionInfo],
    annotated_contracts: dict[str, str],
    memory_model: str,
    config_path: Path,
    project_root: Path,
    writer_script: Path,
    project_directory: str,
    writer_timeout: int = 3000,
) -> dict[str, list[str]]:
    """Generate class invariant annotations for each class with an __init__.

    For each class found in the source, extract its __init__ body and field
    information, then call the writer pipeline to generate appropriate
    ``#@ class invariant`` expressions.

    Returns:
        Mapping from class name to a list of invariant expression strings
        (without the ``#@ class invariant`` prefix).
    """
    tree = ast.parse(source)
    source_lines = source.splitlines(keepends=True)
    class_invariants: dict[str, list[str]] = {}

    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Find __init__
        init_node = None
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                init_node = child
                break
        if init_node is None:
            continue

        # Extract __init__ source
        init_start = init_node.lineno - 1
        init_end = init_node.end_lineno or init_node.lineno
        init_source = "".join(source_lines[init_start:init_end])

        # Collect annotated method contracts for context
        method_contracts_parts = []
        for f in functions:
            if f.class_name == node.name and f.contracts:
                method_contracts_parts.append(
                    f"# Contracts for {f.name}:\n{f.contracts}"
                )
        method_contracts = "\n\n".join(method_contracts_parts)

        # Build a synthetic function_source that is the __init__
        # The class_context tells the writer what fields exist
        class_ctx = _extract_class_context(source, node.name)

        try:
            log(project_directory, AGENT_NAME,
                f"Generating class invariant for {node.name}")
            result = _invoke_writer(
                function_source=init_source,
                callee_contracts=method_contracts,
                class_context=(
                    class_ctx
                    + "\n\n# IMPORTANT: This is __init__. Your MAIN task is to "
                    "generate one or more `#@ class invariant <expr>` lines "
                    "that capture the key properties this class must maintain. "
                    "Place them immediately before the `def __init__` line. "
                    "Use ONLY expressions involving `self.<field>` and integer "
                    "comparisons (e.g. `self._balance >= 0`, "
                    "`self._lo <= self._hi`). "
                    "For requires/ensures on __init__, use `requires 1 == 1` "
                    "and `ensures 1 == 1`."
                ),
                memory_model=memory_model,
                config_path=config_path,
                project_root=project_root,
                writer_script=writer_script,
                    writer_timeout=writer_timeout,
            )

            # Parse the result for #@ class invariant lines
            inv_exprs = []
            for line in result.splitlines():
                m = re.match(r'^\s*#@\s*class invariant\s+(.+)$', line.strip())
                if m:
                    expr = m.group(1).strip()
                    if expr and expr != '1 == 1':
                        inv_exprs.append(expr)

            if inv_exprs:
                class_invariants[node.name] = inv_exprs
                log(project_directory, AGENT_NAME,
                    f"Class {node.name}: generated {len(inv_exprs)} invariant(s)")
            else:
                log(project_directory, AGENT_NAME,
                    f"Class {node.name}: no invariants generated")

        except Exception as e:
            log(project_directory, AGENT_NAME,
                f"Class invariant generation failed for {node.name}: {e}")

    return class_invariants


def _fix_annotation_indentation(annotated_source: str) -> str:
    """Ensure #@ annotation lines have the same indentation as the def they precede.

    LLMs sometimes emit contracts at column 0 even when the function is indented
    inside a class. This fixes that by aligning all contiguous #@ blocks to the
    indent of the next non-annotation line (usually `def`).
    """
    lines = annotated_source.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("#@"):
            # Collect contiguous #@ block
            block_start = i
            while i < len(lines) and lines[i].strip().startswith("#@"):
                i += 1
            # Find target indentation from next non-blank line
            target_indent = ""
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                target_indent = re.match(r'^(\s*)', lines[j]).group(1)
            # Re-indent the #@ block
            for k in range(block_start, i):
                stripped = lines[k].strip()
                result.append(f"{target_indent}{stripped}\n")
        else:
            result.append(lines[i])
            i += 1
    return "".join(result)


def _reassemble_file(
    original_source: str,
    functions: list[FunctionInfo],
    class_invariants: dict[str, list[str]] | None = None,
) -> str:
    """Replace original function sources with their annotated versions
    and insert class invariant annotations before class definitions."""
    source_lines = original_source.splitlines(keepends=True)

    # Insert class invariants before class definitions (process bottom-up
    # to avoid index shifts)
    if class_invariants:
        tree = ast.parse(original_source)
        class_defs = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef) and node.name in class_invariants:
                class_defs.append((node.lineno, node.name))
        # Sort descending by line number
        for lineno, cname in sorted(class_defs, reverse=True):
            inv_lines = class_invariants[cname]
            # Detect indentation of the class line
            class_line = source_lines[lineno - 1]
            indent = re.match(r'^(\s*)', class_line).group(1)
            inv_text = "".join(f"{indent}#@ class invariant {inv}\n"
                               for inv in inv_lines)
            source_lines.insert(lineno - 1, inv_text)

    # Sort functions by start_line descending so replacements don't shift indices
    sorted_funcs = sorted(functions, key=lambda f: f.start_line, reverse=True)

    for info in sorted_funcs:
        if info.annotated_source is None:
            continue
        # Fix indentation of #@ lines to match the def line indentation
        annotated_fixed = _fix_annotation_indentation(info.annotated_source)
        # Replace lines [start_line-1 : end_line] with annotated source
        annotated_lines = annotated_fixed.splitlines(keepends=True)
        # Ensure trailing newline
        if annotated_lines and not annotated_lines[-1].endswith("\n"):
            annotated_lines[-1] += "\n"
        source_lines[info.start_line - 1 : info.end_line] = annotated_lines

    return "".join(source_lines)


# ---------------------------------------------------------------------------
# Module-level brief (R1 — deterministic extraction)
# ---------------------------------------------------------------------------

def _generate_module_brief(source: str) -> str:
    """Extract a deterministic module-level brief from the Python source.

    Collects the module docstring, class names with docstrings/init signatures,
    top-level function signatures, and key imports to give sub-agents context
    about the overall file purpose and architecture.
    """
    tree = ast.parse(source)
    parts = []

    # Module docstring
    if (isinstance(tree.body[0], ast.Expr) and
            isinstance(tree.body[0].value, ast.Constant)):
        docstr = tree.body[0].value.value
        if isinstance(docstr, str):
            parts.append(f"Module docstring:\n{docstr.strip()}\n")

    # Imports
    imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                imports.append(f"{mod}.{alias.name}")
    if imports:
        parts.append("Key imports: " + ", ".join(imports[:20]))

    # Classes
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_desc = f"class {node.name}"
            if node.bases:
                base_names = []
                for b in node.bases:
                    if isinstance(b, ast.Name):
                        base_names.append(b.id)
                    elif isinstance(b, ast.Attribute):
                        base_names.append(ast.dump(b))
                if base_names:
                    class_desc += f"({', '.join(base_names)})"
            # Class docstring
            if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant)):
                docstr = node.body[0].value.value
                if isinstance(docstr, str):
                    class_desc += f" — {docstr.strip()[:200]}"
            # __init__ signature
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                    args = [a.arg for a in child.args.args if a.arg != "self"]
                    class_desc += f"\n  __init__ params: {', '.join(args) if args else '(none)'}"
                    # Collect self.xxx assignments for field listing
                    fields = set()
                    for stmt in ast.walk(child):
                        if (isinstance(stmt, ast.Assign) and stmt.targets and
                                isinstance(stmt.targets[0], ast.Attribute) and
                                isinstance(stmt.targets[0].value, ast.Name) and
                                stmt.targets[0].value.id == "self"):
                            fields.add(stmt.targets[0].attr)
                    if fields:
                        class_desc += f"\n  Fields: {', '.join(sorted(fields)[:30])}"
                    break
            # Method count
            methods = [c for c in node.body if isinstance(c, ast.FunctionDef)]
            class_desc += f"\n  Methods: {len(methods)}"
            parts.append(class_desc)

    # Top-level functions
    top_funcs = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            sig = f"def {node.name}("
            args = [a.arg for a in node.args.args]
            sig += ", ".join(args) + ")"
            top_funcs.append(sig)
    if top_funcs:
        parts.append("Top-level functions:\n  " + "\n  ".join(top_funcs[:30]))

    return "\n\n".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# Writer invocation
# ---------------------------------------------------------------------------

def _invoke_writer(
    function_source: str,
    callee_contracts: str,
    class_context: str,
    memory_model: str,
    config_path: Path,
    project_root: Path,
    writer_script: Path,
    module_brief: str = "",
    callee_sources: str = "",
    catalog_seed: str = "",
    assigns_hint: str = "",
    formal_model_hint: str = "",
    writer_timeout: int = 3000,
) -> str:
    """Call agent-writer.py as a subprocess to annotate a single function."""
    cmd = [
        sys.executable,
        str(writer_script),
        "--memory-model", memory_model,
        "--config", str(config_path),
    ]

    # Pass data via stdin as JSON
    payload = {
        "function_source": function_source,
        "callee_contracts": callee_contracts,
        "class_context": class_context,
    }
    if module_brief:
        payload["module_brief"] = module_brief
    if callee_sources:
        payload["callee_sources"] = callee_sources
    if catalog_seed:
        payload["catalog_seed"] = catalog_seed
    if assigns_hint:
        payload["assigns_hint"] = assigns_hint
    if formal_model_hint:
        payload["formal_model_hint"] = formal_model_hint

    input_data = json.dumps(payload)

    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
        cwd=str(project_root),
        timeout=writer_timeout,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"agent-writer failed (exit {result.returncode}): {result.stderr[:500]}"
        )

    # Strip any #@ \trusted lines — the pipeline must never emit them
    output = re.sub(r'^\s*#@\s*\\trusted\s*\n', '', result.stdout,
                    flags=re.MULTILINE)
    return output


def _body_preserved(original: str, annotated: str) -> bool:
    """Check that the annotated version still contains the function body.

    Strips all ``#@`` annotation lines and blank lines from both strings,
    then verifies that the core body lines of the original appear in the
    annotated output.  This catches cases where the LLM accidentally
    deletes or rewrites the implementation.
    """
    def _strip_annotations(text: str) -> list[str]:
        return [
            line.rstrip()
            for line in text.splitlines()
            if line.strip() and not line.strip().startswith("#@")
        ]

    orig_body = _strip_annotations(original)
    ann_body = _strip_annotations(annotated)

    if not orig_body:
        return True

    # The annotated version should contain at least 80% of the original lines
    matched = sum(1 for line in orig_body if line in ann_body)
    return matched >= len(orig_body) * 0.8


def _safe_fallback_annotation(info: FunctionInfo) -> str:
    """Return the function with trivially-true contracts as a safe fallback."""
    lines = info.source.splitlines(keepends=True)
    # Find the def line
    indent = ""
    for i, line in enumerate(lines):
        if re.match(r'^(\s*)def\s+', line):
            indent = re.match(r'^(\s*)', line).group(1)
            break

    is_method = info.class_name is not None and not info.is_dunder
    assigns_line = f"{indent}#@ assigns \\nothing\n"
    if is_method:
        # Try to detect field mutations
        field_mutates = re.findall(r'\bself\.(\w+)\s*(?:=|\+=|-=|\*=)', info.source)
        if field_mutates:
            seen = []
            assigns_parts = []
            for fld in field_mutates:
                if fld not in seen:
                    seen.append(fld)
                    assigns_parts.append(f"{indent}#@ assigns self.{fld}\n")
            assigns_line = "".join(assigns_parts)

    contracts = (
        f"{indent}#@ requires 1 == 1\n"
        f"{indent}#@ ensures 1 == 1\n"
        f"{assigns_line}"
    )

    # Insert before the def line
    for i, line in enumerate(lines):
        if re.match(r'^\s*def\s+', line):
            lines.insert(i, contracts)
            break

    return "".join(lines)


def _compute_assigns_hint(
    info: FunctionInfo,
    annotatable_map: dict,
    visited: Optional[set] = None,
) -> list[str]:
    """Static analysis: find all self._ attributes assigned in the function
    body and transitively in callee bodies.

    Returns a deduplicated sorted list of field names like
    ``["_array_locals", "_dict_locals", ...]``.
    """
    if visited is None:
        visited = set()
    if info.name in visited:
        return []
    visited.add(info.name)

    fields = re.findall(r'\bself\.(\w+)\s*(?:=|\+=|-=|\*=)', info.source)

    # Walk callees transitively
    for callee_name in info.callees:
        if callee_name in annotatable_map:
            callee_info = annotatable_map[callee_name]
            fields.extend(
                _compute_assigns_hint(callee_info, annotatable_map, visited)
            )

    return sorted(set(fields))


def _format_assigns_hint(fields: list[str]) -> str:
    """Format an assigns hint for the contract-writer prompt."""
    if not fields:
        return ""
    field_list = ", ".join(f"self.{f}" for f in fields)
    return (
        f"Static analysis detected the following self._ fields are mutated "
        f"(directly or via callees): {field_list}. "
        f"Use this as the basis for #@ assigns clauses."
    )
    """Check that the annotated source still contains the original function body.

    Rejects output where:
    - The body was replaced with `pass`
    - Total non-annotation lines shrunk to less than 60% of original
    """
    orig_code_lines = [
        l for l in original_source.splitlines()
        if l.strip() and not l.strip().startswith("#@")
    ]
    ann_code_lines = [
        l for l in annotated_source.splitlines()
        if l.strip() and not l.strip().startswith("#@")
    ]

    if not orig_code_lines:
        return True

    # Check for body replaced with `pass`
    # Count non-def, non-decorator code lines in annotated output
    ann_body_lines = [
        l for l in ann_code_lines
        if not re.match(r'^\s*(def\s|@)', l)
    ]
    if len(ann_body_lines) == 1 and ann_body_lines[0].strip() == 'pass':
        orig_body_lines = [
            l for l in orig_code_lines
            if not re.match(r'^\s*(def\s|@)', l)
        ]
        if len(orig_body_lines) > 1:
            return False  # body was stripped

    # Check line count ratio
    ratio = len(ann_code_lines) / len(orig_code_lines)
    if ratio < 0.6:
        return False

    return True


def _validate_pycsl_syntax(
    annotated_source: str,
    project_root: Path,
    project_directory: str,
    class_name: Optional[str] = None,
    class_invariants_list: Optional[list] = None,
    original_source: str = "",
) -> bool:
    """Run pycsl --no-proof on the annotated source to check for syntax errors.

    When the function is a method, wraps it in a minimal class shell with
    imports so that pycsl can parse it.

    Returns True if the contracts parse without errors, False otherwise.
    """
    import tempfile
    import textwrap

    pycsl_script = project_root / "src" / "pycsl" / "pycsl.py"
    if not pycsl_script.exists():
        return True  # can't validate, assume OK

    # Build a compilable file for validation
    file_parts = []

    # Collect imports from the original source file
    if original_source:
        for line in original_source.splitlines():
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                file_parts.append(line)
        if file_parts:
            file_parts.append("")

    # If no imports found, add common typing imports
    if not file_parts:
        file_parts.append(
            "from typing import Dict, List, Any, Optional, Set, Tuple, Union"
        )
        file_parts.append("")

    if class_name:
        # Wrap in class shell
        inv_lines = ""
        if class_invariants_list:
            inv_lines = "\n".join(
                f"    #@ class invariant {e}" for e in class_invariants_list
            )
            inv_lines += "\n"
        file_parts.append(f"class {class_name}:")
        if inv_lines:
            file_parts.append(inv_lines)
        # Indent the annotated source to be a method body
        indented = textwrap.indent(annotated_source, "    ")
        file_parts.append(indented)
    else:
        file_parts.append(annotated_source)

    file_content = "\n".join(file_parts)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        result = subprocess.run(
            [sys.executable, str(pycsl_script), "--no-proof", tmp_path],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=60,
        )

        import os
        os.unlink(tmp_path)

        if result.returncode != 0:
            err_msg = (result.stderr or result.stdout or "unknown error")[:300]
            log(project_directory, AGENT_NAME,
                f"PyCSL validation failed: {err_msg}")
            return False
        return True
    except Exception as e:
        log(project_directory, AGENT_NAME,
            f"PyCSL validation error: {e}")
        return True  # can't validate, assume OK


def _checkpoint_save(
    cache_dir: Path,
    func_name: str,
    annotated_source: str,
    contracts: str,
) -> None:
    """Persist one function's annotation to the checkpoint cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_name = func_name.replace(".", "__")
    entry = {"annotated_source": annotated_source, "contracts": contracts}
    (cache_dir / f"{safe_name}.json").write_text(
        json.dumps(entry, ensure_ascii=False), encoding="utf-8"
    )


def _checkpoint_load(
    cache_dir: Path,
    func_name: str,
) -> Optional[dict]:
    """Load a previously checkpointed annotation, or None."""
    safe_name = func_name.replace(".", "__")
    path = cache_dir / f"{safe_name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None

# Main orchestration
# ---------------------------------------------------------------------------

def _matches_filter(
    info: FunctionInfo,
    filter_class: Optional[str],
    filter_func: Optional[str],
) -> bool:
    """Check if a function matches the --class/--fun filter.

    Returns True if the function should be annotated (i.e. it matches the
    filter or no filter was specified).
    """
    if filter_class is None and filter_func is None:
        return True
    short_name = info.name.split(".")[-1]
    if filter_class and filter_func:
        return info.class_name == filter_class and short_name == filter_func
    if filter_class:
        return info.class_name == filter_class
    # filter_func only
    return short_name == filter_func


def _lookup_catalog_seed(
    info: FunctionInfo,
    catalog_data: dict[str, dict],
) -> str:
    """Look up a function in the JSON catalog and return seed text.

    Returns a formatted string with the pre-generated English description and
    PyCSL contracts, or empty string if not found.
    """
    if not catalog_data:
        return ""
    short_name = info.name.split(".")[-1]
    # Try qualified lookup: class_name -> method_name
    if info.class_name and info.class_name in catalog_data:
        entry = catalog_data[info.class_name].get(short_name)
        if entry:
            parts = []
            eng = entry.get("english", "")
            pycsl = entry.get("pycsl", "")
            if eng:
                parts.append(f"Pre-generated English description:\n{eng}")
            if pycsl:
                parts.append(f"Pre-generated PyCSL contracts:\n{pycsl}")
            return "\n\n".join(parts) if parts else ""
    # Try module-level lookup: "_module" -> function_name
    if not info.class_name and "_module" in catalog_data:
        entry = catalog_data["_module"].get(short_name)
        if entry:
            parts = []
            eng = entry.get("english", "")
            pycsl = entry.get("pycsl", "")
            if eng:
                parts.append(f"Pre-generated English description:\n{eng}")
            if pycsl:
                parts.append(f"Pre-generated PyCSL contracts:\n{pycsl}")
            return "\n\n".join(parts) if parts else ""
    return ""


def _lookup_formal_model_hint(
    info: FunctionInfo,
    catalog_data: dict[str, dict],
) -> str:
    """Extract the 'english' field from the JSON catalog for formal model context.

    Returns the pre-generated English description (which may contain formal
    model references like WP rules), or empty string if not found.
    """
    if not catalog_data:
        return ""
    short_name = info.name.split(".")[-1]
    entry = None
    if info.class_name and info.class_name in catalog_data:
        entry = catalog_data[info.class_name].get(short_name)
    elif not info.class_name and "_module" in catalog_data:
        entry = catalog_data["_module"].get(short_name)
    if entry:
        return entry.get("english", "")
    return ""


def run_splitter(
    input_path: Path,
    output_path: Path,
    config_path: Path,
    project_root: Path,
    memory_model: str = "hoare",
    project_directory: str = ".",
    filter_class: Optional[str] = None,
    filter_func: Optional[str] = None,
    resume: bool = False,
    verbose: bool = False,
    writer_timeout: int = 3000,
) -> str:
    """Run the full split-annotate pipeline and return the annotated source.

    If *filter_class* and/or *filter_func* are given, only matching functions
    are sent to the writer for annotation.  The call-graph analysis still runs
    on the full file so that callee contracts are available as context.

    If *resume* is True, load previously checkpointed per-function results
    from ``<output_dir>/.splitter-cache/`` and skip already-annotated
    functions.
    """
    writer_script = Path(__file__).parent / "agent-writer.py"

    source = input_path.read_text(encoding="utf-8")
    log(project_directory, AGENT_NAME, f"Parsing {input_path} ({len(source)} chars)")

    # Checkpoint directory: sits next to the output file
    cache_dir = output_path.parent / ".splitter-cache"

    # Step 1: Extract functions and build call graph
    functions, func_map = _extract_functions(source)
    _build_call_graph(functions, func_map)

    log(project_directory, AGENT_NAME,
        f"Found {len(functions)} functions/methods, "
        f"call graph edges: {sum(len(f.callees) for f in functions)}")

    # Filter out dunders and properties (Module5 skips them)
    annotatable = [f for f in functions if not f.is_dunder and not f.is_property]
    annotatable_map = {f.name: f for f in annotatable}

    if filter_class or filter_func:
        target_names = [f.name for f in annotatable
                        if _matches_filter(f, filter_class, filter_func)]
        if not target_names:
            # Try a fuzzy match: if --fun is given, search across all classes
            if filter_func:
                all_matches = [f for f in annotatable
                               if f.name.split(".")[-1] == filter_func]
                if all_matches:
                    found_in = ", ".join(
                        f"{f.class_name or '(top-level)'}.{f.name.split('.')[-1]}"
                        for f in all_matches
                    )
                    log(project_directory, AGENT_NAME,
                        f"No functions match filter (class={filter_class}, fun={filter_func}). "
                        f"Did you mean? {found_in}")
                    # Auto-correct: use the first match
                    target_names = [all_matches[0].name]
                    filter_class = all_matches[0].class_name
                    log(project_directory, AGENT_NAME,
                        f"Auto-corrected to class={filter_class}, annotating: {target_names}")
                else:
                    # List available classes and sample functions
                    classes = sorted(set(
                        f.class_name for f in annotatable if f.class_name
                    ))
                    top_funcs = sorted(set(
                        f.name.split(".")[-1] for f in annotatable
                        if not f.class_name
                    ))[:10]
                    log(project_directory, AGENT_NAME,
                        f"No functions match filter (class={filter_class}, fun={filter_func}). "
                        f"Available classes: {classes}. "
                        f"Top-level functions: {top_funcs}")
                    return source
            else:
                # Only --class given but no match
                classes = sorted(set(
                    f.class_name for f in annotatable if f.class_name
                ))
                log(project_directory, AGENT_NAME,
                    f"No functions match filter (class={filter_class}). "
                    f"Available classes: {classes}")
                return source
        log(project_directory, AGENT_NAME,
            f"Filter active — will annotate: {target_names}")

    if not annotatable:
        log(project_directory, AGENT_NAME, "No annotatable functions found, returning original")
        return source

    # Step 2a: Generate module-level brief (R1)
    module_brief = _generate_module_brief(source)
    if module_brief:
        log(project_directory, AGENT_NAME,
            f"Module brief generated ({len(module_brief)} chars)")

    # Step 2a-bis: Load JSON catalog seed if available (R5)
    catalog_data: dict[str, dict] = {}
    catalog_dir = project_root / "src" / "self-annotate" / "src"
    if catalog_dir.is_dir():
        stem = input_path.stem  # e.g. "Module6_WhyMLTranspiler"
        catalog_path = catalog_dir / f"{stem}.json"
        if catalog_path.exists():
            try:
                catalog_data = json.loads(catalog_path.read_text(encoding="utf-8"))
                total = sum(len(v) for v in catalog_data.values())
                log(project_directory, AGENT_NAME,
                    f"Loaded catalog seed: {catalog_path.name} ({total} entries)")
            except (json.JSONDecodeError, OSError):
                pass

    # Step 2b: Generate class invariants BEFORE annotating methods.
    # Methods need to see the invariant to generate proper guarding `requires`.
    # When a filter is active, only generate invariants for the target class.
    if filter_class:
        # Only generate class invariants for the target class
        target_class_funcs = [f for f in functions if f.class_name == filter_class]
        class_invariants = _generate_class_invariants(
            source, target_class_funcs, {},
            memory_model, config_path, project_root, writer_script,
            project_directory, writer_timeout=writer_timeout,
        )
    elif filter_func and not filter_class:
        # --fun only: skip class invariant generation entirely (expensive LLM call)
        class_invariants = {}
    else:
        class_invariants = _generate_class_invariants(
            source, functions, {},
            memory_model, config_path, project_root, writer_script,
            project_directory, writer_timeout=writer_timeout,
        )

    # Step 3: Detect SCCs and topological order
    sccs = _tarjan_scc(annotatable_map)
    log(project_directory, AGENT_NAME,
        f"Topological order: {len(sccs)} groups "
        f"(SCCs with >1 member: {sum(1 for s in sccs if len(s) > 1)})")

    # Step 4: Annotate in topological order (leaves first)
    annotated_contracts: dict[str, str] = {}  # qname -> contract text
    total_to_annotate = sum(
        len([annotatable_map[n] for n in scc if n in annotatable_map])
        for scc in sccs
    )
    progress_counter = 0
    resumed_count = 0
    annotation_start_time = time.monotonic()

    # Startup summary on stderr
    scc_multi = sum(1 for s in sccs if len(s) > 1)
    est_minutes = total_to_annotate * 2.5  # ~2.5 min/function empirical
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"  File:      {input_path}", file=sys.stderr)
    print(f"  Functions: {total_to_annotate}", file=sys.stderr)
    print(f"  SCCs:      {len(sccs)} groups ({scc_multi} with >1 member)", file=sys.stderr)
    if filter_class or filter_func:
        print(f"  Filter:    class={filter_class or '*'} fun={filter_func or '*'}",
              file=sys.stderr)
    print(f"  Est. time: ~{int(est_minutes)} min ({est_minutes/60:.1f} hrs)",
          file=sys.stderr)
    print(f"  Timeout:   {writer_timeout}s per function", file=sys.stderr)
    print(f"{'─'*60}\n", file=sys.stderr)

    # Load checkpointed results when --resume is active
    if resume and cache_dir.is_dir():
        for info in annotatable:
            cached = _checkpoint_load(cache_dir, info.name)
            if cached:
                info.annotated_source = cached["annotated_source"]
                info.contracts = cached.get("contracts", "")
                annotated_contracts[info.name] = info.contracts
                resumed_count += 1
        if resumed_count:
            log(project_directory, AGENT_NAME,
                f"Resumed {resumed_count} functions from checkpoint cache")
            print(f"Resumed {resumed_count}/{total_to_annotate} functions from cache",
                  file=sys.stderr)

    _interrupted = False
    for scc in sccs:
        if _interrupted:
            break
        # Filter to only functions we track
        scc_funcs = [annotatable_map[n] for n in scc if n in annotatable_map]
        if not scc_funcs:
            continue

        # Collect callee contracts for context
        all_callees = set()
        for f in scc_funcs:
            all_callees.update(f.callees)
        # Exclude self-references within this SCC
        scc_names = set(scc)
        external_callees = all_callees - scc_names

        callee_context_parts = []
        for callee_name in sorted(external_callees):
            if callee_name in annotated_contracts:
                callee_context_parts.append(
                    f"# Contracts for {callee_name}:\n{annotated_contracts[callee_name]}"
                )

        callee_contracts = "\n\n".join(callee_context_parts)

        # Collect callee source snippets for the english-writer (R3)
        callee_source_parts = []
        for callee_name in sorted(external_callees):
            if callee_name in annotatable_map:
                callee_info = annotatable_map[callee_name]
                # Include first ~15 lines (signature + docstring)
                src_lines = callee_info.source.splitlines()
                snippet = "\n".join(src_lines[:15])
                if len(src_lines) > 15:
                    snippet += "\n    ..."
                callee_source_parts.append(
                    f"# Source for {callee_name}:\n{snippet}"
                )
        callee_sources = "\n\n".join(callee_source_parts[:10])

        # When a filter is active, skip functions that don't match.
        # We still process them through the loop so their callee contracts
        # accumulate, but we don't invoke the writer — just leave them
        # unannotated (original source passes through in reassembly).
        if filter_class is not None or filter_func is not None:
            scc_funcs = [f for f in scc_funcs
                         if _matches_filter(f, filter_class, filter_func)]
            if not scc_funcs:
                continue

        if len(scc_funcs) == 1:
            info = scc_funcs[0]
            progress_counter += 1

            # Skip if already loaded from checkpoint
            if info.name in annotated_contracts and resume:
                log(project_directory, AGENT_NAME,
                    f"Skipping (cached): {info.name}")
                print(f"[{progress_counter}/{total_to_annotate}] Cached: {info.name}",
                      file=sys.stderr)
                continue

            fn_start = time.monotonic()
            elapsed_total = fn_start - annotation_start_time
            log(project_directory, AGENT_NAME, f"Annotating: {info.name}")
            print(f"[{progress_counter}/{total_to_annotate}] "
                  f"({int(elapsed_total)}s elapsed) Annotating: {info.name}",
                  file=sys.stderr)

            # Get class context if it's a method
            class_ctx = ""
            if info.class_name:
                class_ctx = _extract_class_context(source, info.class_name)
                # Inject generated class invariants so the writer sees them
                if info.class_name in class_invariants:
                    inv_lines = "\n".join(
                        f"#@ class invariant {e}"
                        for e in class_invariants[info.class_name]
                    )
                    class_ctx = inv_lines + "\n" + class_ctx

            try:
                seed = _lookup_catalog_seed(info, catalog_data)
                fm_hint = _lookup_formal_model_hint(info, catalog_data)
                # Compute assigns hint from static analysis
                assigns_fields = _compute_assigns_hint(info, annotatable_map)
                hint = _format_assigns_hint(assigns_fields)
                if verbose:
                    print(f"    catalog_seed: {'yes' if seed else 'no'}, "
                          f"formal_model: {'yes' if fm_hint else 'no'}, "
                          f"assigns: {assigns_fields or '(none)'}, "
                          f"callees: {len(callee_contracts)} chars",
                          file=sys.stderr)
                annotated = _invoke_writer(
                    function_source=info.source,
                    callee_contracts=callee_contracts,
                    class_context=class_ctx,
                    memory_model=memory_model,
                    config_path=config_path,
                    project_root=project_root,
                    writer_script=writer_script,
                    module_brief=module_brief,
                    callee_sources=callee_sources,
                    catalog_seed=seed,
                    assigns_hint=hint,
                    formal_model_hint=fm_hint,
                    writer_timeout=writer_timeout,
                )
                annotated = annotated.strip()
                if not annotated:
                    raise RuntimeError("Empty response from writer")
                if not _body_preserved(info.source, annotated):
                    log(project_directory, AGENT_NAME,
                        f"Body stripped for {info.name}, using safe fallback")
                    raise RuntimeError("Body was stripped by LLM")
                valid = _validate_pycsl_syntax(
                    annotated, project_root, project_directory,
                    class_name=info.class_name,
                    class_invariants_list=class_invariants.get(info.class_name),
                    original_source=source,
                )
                if verbose:
                    print(f"    validation: {'PASS' if valid else 'FAIL'}",
                          file=sys.stderr)
                if not valid:
                    # Retry once with repair context
                    log(project_directory, AGENT_NAME,
                        f"Validation failed for {info.name}, retrying with repair prompt")
                    print(f"[{progress_counter}/{total_to_annotate}] Retrying: {info.name}",
                          file=sys.stderr)
                    annotated = _invoke_writer(
                        function_source=info.source,
                        callee_contracts=callee_contracts + "\n\n## REPAIR\n"
                            "The previous annotation failed PyCSL syntax validation. "
                            "Fix the contracts. Do NOT use #@ \\trusted. "
                            "Ensure every #@ line uses valid PyCSL syntax.",
                        class_context=class_ctx,
                        memory_model=memory_model,
                        config_path=config_path,
                        project_root=project_root,
                        writer_script=writer_script,
                        module_brief=module_brief,
                        callee_sources=callee_sources,
                        catalog_seed=seed,
                        assigns_hint=hint,
                        formal_model_hint=fm_hint,
                        writer_timeout=writer_timeout,
                    ).strip()
                    if not annotated or not _body_preserved(info.source, annotated):
                        raise RuntimeError("Repair attempt failed: empty or body stripped")
                    if not _validate_pycsl_syntax(
                        annotated, project_root, project_directory,
                        class_name=info.class_name,
                        class_invariants_list=class_invariants.get(info.class_name),
                        original_source=source,
                    ):
                        log(project_directory, AGENT_NAME,
                            f"PyCSL validation failed after retry for {info.name}")
                        print(f"WARNING: PyCSL validation failed for {info.name} "
                              f"after retry, using safe fallback", file=sys.stderr)
                        raise RuntimeError("PyCSL syntax validation failed after retry")
                info.annotated_source = annotated
                info.contracts = _extract_contracts_text(annotated)
                annotated_contracts[info.name] = info.contracts
                _checkpoint_save(cache_dir, info.name,
                                 annotated, info.contracts)
                fn_elapsed = time.monotonic() - fn_start
                print(f"    ✓ {info.name} ({int(fn_elapsed)}s)", file=sys.stderr)
            except Exception as e:
                fn_elapsed = time.monotonic() - fn_start
                log(project_directory, AGENT_NAME,
                    f"Writer failed for {info.name}: {e}, using safe fallback")
                print(f"    ✗ {info.name}: {e} ({int(fn_elapsed)}s, safe fallback)",
                      file=sys.stderr)
                info.annotated_source = _safe_fallback_annotation(info)
                info.contracts = _extract_contracts_text(info.annotated_source)
                annotated_contracts[info.name] = info.contracts
            except KeyboardInterrupt:
                log(project_directory, AGENT_NAME,
                    f"Interrupted during {info.name}, saving partial output")
                print(f"\n⚠ Interrupted! Saving partial output "
                      f"({progress_counter}/{total_to_annotate} done)…",
                      file=sys.stderr)
                _interrupted = True
                break

        elif len(scc_funcs) <= 3:
            # Small mutual recursion group — send all together
            progress_counter += len(scc_funcs)
            log(project_directory, AGENT_NAME,
                f"Annotating SCC group: {[f.name for f in scc_funcs]}")
            print(f"[{progress_counter}/{total_to_annotate}] Annotating SCC group: "
                  f"{[f.name for f in scc_funcs]}", file=sys.stderr)
            combined_source = "\n\n".join(f.source for f in scc_funcs)

            class_ctx = ""
            class_names = {f.class_name for f in scc_funcs if f.class_name}
            if class_names:
                parts = []
                for cn in class_names:
                    ctx = _extract_class_context(source, cn)
                    if cn in class_invariants:
                        inv_lines = "\n".join(
                            f"#@ class invariant {e}"
                            for e in class_invariants[cn]
                        )
                        ctx = inv_lines + "\n" + ctx
                    parts.append(ctx)
                class_ctx = "\n\n".join(parts)

            try:
                # For SCC groups, concatenate catalog seeds for all functions
                scc_seeds = []
                for f in scc_funcs:
                    s = _lookup_catalog_seed(f, catalog_data)
                    if s:
                        scc_seeds.append(f"--- {f.name} ---\n{s}")
                combined_seed = "\n\n".join(scc_seeds)
                annotated = _invoke_writer(
                    function_source=combined_source,
                    callee_contracts=callee_contracts,
                    class_context=class_ctx,
                    memory_model=memory_model,
                    config_path=config_path,
                    project_root=project_root,
                    writer_script=writer_script,
                    module_brief=module_brief,
                    callee_sources=callee_sources,
                    catalog_seed=combined_seed,
                    writer_timeout=writer_timeout,
                )
                annotated = annotated.strip()
                if not annotated:
                    raise RuntimeError("Empty response from writer")

                # Parse the combined annotated output to split per-function
                annotated_funcs = _split_annotated_functions(annotated, scc_funcs)
                for info in scc_funcs:
                    if info.name in annotated_funcs:
                        func_annotated = annotated_funcs[info.name]
                        if not _body_preserved(info.source, func_annotated):
                            log(project_directory, AGENT_NAME,
                                f"Body stripped for {info.name} in SCC, using fallback")
                            info.annotated_source = _safe_fallback_annotation(info)
                        elif not _validate_pycsl_syntax(
                            func_annotated, project_root, project_directory,
                            class_name=info.class_name,
                            class_invariants_list=class_invariants.get(
                                info.class_name),
                            original_source=source,
                        ):
                            log(project_directory, AGENT_NAME,
                                f"PyCSL validation failed for {info.name} in SCC, "
                                f"using fallback")
                            print(f"WARNING: PyCSL validation failed for "
                                  f"{info.name}, using safe fallback",
                                  file=sys.stderr)
                            info.annotated_source = _safe_fallback_annotation(info)
                        else:
                            info.annotated_source = func_annotated
                        info.contracts = _extract_contracts_text(info.annotated_source)
                        annotated_contracts[info.name] = info.contracts
                        _checkpoint_save(cache_dir, info.name,
                                         info.annotated_source, info.contracts)
                    else:
                        info.annotated_source = _safe_fallback_annotation(info)
                        info.contracts = _extract_contracts_text(info.annotated_source)
                        annotated_contracts[info.name] = info.contracts
            except Exception as e:
                log(project_directory, AGENT_NAME,
                    f"Writer failed for SCC {[f.name for f in scc_funcs]}: {e}, using fallback")
                for info in scc_funcs:
                    info.annotated_source = _safe_fallback_annotation(info)
                    info.contracts = _extract_contracts_text(info.annotated_source)
                    annotated_contracts[info.name] = info.contracts
        else:
            # Large SCC — annotate each member individually.
            # Pass SCC-mate signatures as additional callee context so the
            # writer knows the contracts of co-recursive functions.
            log(project_directory, AGENT_NAME,
                f"Large SCC ({len(scc_funcs)} functions), annotating individually: "
                f"{[f.name for f in scc_funcs]}")

            for info in scc_funcs:
                progress_counter += 1

                # Skip if already loaded from checkpoint
                if info.name in annotated_contracts and resume:
                    log(project_directory, AGENT_NAME,
                        f"Skipping (cached): {info.name}")
                    print(f"[{progress_counter}/{total_to_annotate}] Cached: {info.name}",
                          file=sys.stderr)
                    continue

                fn_start = time.monotonic()
                elapsed_total = fn_start - annotation_start_time
                log(project_directory, AGENT_NAME,
                    f"Annotating (SCC member): {info.name}")
                print(f"[{progress_counter}/{total_to_annotate}] "
                      f"({int(elapsed_total)}s elapsed) Annotating (SCC): {info.name}",
                      file=sys.stderr)

                class_ctx = ""
                if info.class_name:
                    class_ctx = _extract_class_context(source, info.class_name)
                    if info.class_name in class_invariants:
                        inv_lines = "\n".join(
                            f"#@ class invariant {e}"
                            for e in class_invariants[info.class_name]
                        )
                        class_ctx = inv_lines + "\n" + class_ctx

                # Include SCC-mate signatures + any already-annotated
                # contracts as extra callee context
                scc_callee_parts = list(callee_context_parts)
                for mate in scc_funcs:
                    if mate.name == info.name:
                        continue
                    if mate.name in annotated_contracts:
                        scc_callee_parts.append(
                            f"# Contracts for SCC-mate {mate.name}:\n"
                            f"{annotated_contracts[mate.name]}"
                        )
                    else:
                        # Not yet annotated — include signature only
                        sig_lines = mate.source.splitlines()[:3]
                        scc_callee_parts.append(
                            f"# SCC-mate (not yet annotated):\n"
                            + "\n".join(sig_lines)
                        )
                scc_callee_ctx = "\n\n".join(scc_callee_parts)

                try:
                    seed = _lookup_catalog_seed(info, catalog_data)
                    fm_hint = _lookup_formal_model_hint(info, catalog_data)
                    assigns_fields = _compute_assigns_hint(info, annotatable_map)
                    hint = _format_assigns_hint(assigns_fields)
                    annotated = _invoke_writer(
                        function_source=info.source,
                        callee_contracts=scc_callee_ctx,
                        class_context=class_ctx,
                        memory_model=memory_model,
                        config_path=config_path,
                        project_root=project_root,
                        writer_script=writer_script,
                        module_brief=module_brief,
                        callee_sources=callee_sources,
                        catalog_seed=seed,
                        assigns_hint=hint,
                        formal_model_hint=fm_hint,
                        writer_timeout=writer_timeout,
                    )
                    annotated = annotated.strip()
                    if not annotated:
                        raise RuntimeError("Empty response from writer")
                    if not _body_preserved(info.source, annotated):
                        log(project_directory, AGENT_NAME,
                            f"Body stripped for {info.name} in SCC, using safe fallback")
                        raise RuntimeError("Body was stripped by LLM")
                    if not _validate_pycsl_syntax(
                        annotated, project_root, project_directory,
                        class_name=info.class_name,
                        class_invariants_list=class_invariants.get(info.class_name),
                        original_source=source,
                    ):
                        # Retry once with repair context
                        log(project_directory, AGENT_NAME,
                            f"Validation failed for {info.name} in SCC, retrying")
                        print(f"[{progress_counter}/{total_to_annotate}] Retrying: {info.name}",
                              file=sys.stderr)
                        annotated = _invoke_writer(
                            function_source=info.source,
                            callee_contracts=scc_callee_ctx + "\n\n## REPAIR\n"
                                "The previous annotation failed PyCSL syntax validation. "
                                "Fix the contracts. Do NOT use #@ \\trusted. "
                                "Ensure every #@ line uses valid PyCSL syntax.",
                            class_context=class_ctx,
                            memory_model=memory_model,
                            config_path=config_path,
                            project_root=project_root,
                            writer_script=writer_script,
                            module_brief=module_brief,
                            callee_sources=callee_sources,
                            catalog_seed=seed,
                            assigns_hint=hint,
                            formal_model_hint=fm_hint,
                            writer_timeout=writer_timeout,
                        ).strip()
                        if not annotated or not _body_preserved(info.source, annotated):
                            raise RuntimeError("Repair attempt failed in SCC")
                        if not _validate_pycsl_syntax(
                            annotated, project_root, project_directory,
                            class_name=info.class_name,
                            class_invariants_list=class_invariants.get(info.class_name),
                            original_source=source,
                        ):
                            log(project_directory, AGENT_NAME,
                                f"PyCSL validation failed after retry for {info.name}")
                            print(f"WARNING: PyCSL validation failed for {info.name} "
                                  f"after retry, using safe fallback", file=sys.stderr)
                            raise RuntimeError("PyCSL syntax validation failed after retry")
                    info.annotated_source = annotated
                    info.contracts = _extract_contracts_text(annotated)
                    annotated_contracts[info.name] = info.contracts
                    _checkpoint_save(cache_dir, info.name,
                                     annotated, info.contracts)
                    fn_elapsed = time.monotonic() - fn_start
                    print(f"    ✓ {info.name} ({int(fn_elapsed)}s)", file=sys.stderr)
                except Exception as e:
                    fn_elapsed = time.monotonic() - fn_start
                    log(project_directory, AGENT_NAME,
                        f"Writer failed for {info.name}: {e}, using safe fallback")
                    print(f"    ✗ {info.name}: {e} ({int(fn_elapsed)}s, safe fallback)",
                          file=sys.stderr)
                    info.annotated_source = _safe_fallback_annotation(info)
                    info.contracts = _extract_contracts_text(info.annotated_source)
                    annotated_contracts[info.name] = info.contracts
                except KeyboardInterrupt:
                    log(project_directory, AGENT_NAME,
                        f"Interrupted during {info.name}, saving partial output")
                    print(f"\n⚠ Interrupted! Saving partial output "
                          f"({progress_counter}/{total_to_annotate} done)…",
                          file=sys.stderr)
                    _interrupted = True
                    break

    # Print final timing summary
    total_elapsed = time.monotonic() - annotation_start_time
    status = "Interrupted" if _interrupted else "Annotation complete"
    print(f"\n{'─'*60}", file=sys.stderr)
    print(f"  {status}: {progress_counter}/{total_to_annotate} functions "
          f"in {int(total_elapsed)}s ({total_elapsed/60:.1f} min)", file=sys.stderr)
    print(f"{'─'*60}\n", file=sys.stderr)

    # Step 5: Reassemble the file
    result = _reassemble_file(source, annotatable, class_invariants)
    log(project_directory, AGENT_NAME, "File reassembly complete")

    # Step 6: Full-file validation
    try:
        tmp_dir = Path(project_directory) / "tmp_final_validation"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_file = tmp_dir / "final_output.py"
        tmp_file.write_text(result, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-c",
             f"import sys; sys.path.insert(0, '{project_root / 'src' / 'pycsl'}'); "
             f"from pycsl import main as pycsl_main; "
             f"sys.argv = ['pycsl', '--no-proof', '{tmp_file}']; pycsl_main()"],
            capture_output=True, text=True, timeout=120,
            cwd=str(project_root),
        )
        if proc.returncode != 0:
            log(project_directory, AGENT_NAME,
                f"Final file validation WARNING: pycsl --no-proof failed:\n{proc.stderr[:500]}")
            print("WARNING: Final file validation failed (pycsl --no-proof). "
                  "Output file may contain syntax errors.", file=sys.stderr)
        else:
            log(project_directory, AGENT_NAME,
                "Final file validation passed (pycsl --no-proof)")
    except Exception as e:
        log(project_directory, AGENT_NAME,
            f"Final file validation skipped: {e}")
    finally:
        if tmp_dir.exists():
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return result


def _split_annotated_functions(
    annotated_combined: str,
    expected_funcs: list[FunctionInfo],
) -> dict[str, str]:
    """Split a combined annotated output back into per-function text."""
    result: dict[str, str] = {}
    lines = annotated_combined.splitlines(keepends=True)

    # Find all def lines and their positions
    def_positions = []
    for i, line in enumerate(lines):
        m = re.match(r'^(\s*)def\s+(\w+)\s*\(', line)
        if m:
            # Include preceding #@ lines
            start = i
            while start > 0 and lines[start - 1].strip().startswith("#@"):
                start -= 1
            def_positions.append((start, m.group(2)))

    # Map each def to its expected FunctionInfo
    expected_by_short = {}
    for f in expected_funcs:
        short_name = f.name.split(".")[-1]
        expected_by_short[short_name] = f.name

    for idx, (start, func_name) in enumerate(def_positions):
        if idx + 1 < len(def_positions):
            end = def_positions[idx + 1][0]
        else:
            end = len(lines)

        qname = expected_by_short.get(func_name)
        if qname:
            result[qname] = "".join(lines[start:end]).rstrip("\n") + "\n"

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Deterministic call-graph splitter for bottom-up annotation."
    )
    parser.add_argument("--in", dest="in_file", required=True,
                        help="Path to the input Python file.")
    parser.add_argument("--out", dest="out_file", required=True,
                        help="Path to the output annotated file.")
    parser.add_argument("--class", dest="filter_class", default=None,
                        help="Only annotate methods of this class.")
    parser.add_argument("--fun", dest="filter_func", default=None,
                        help="Only annotate function(s) with this name.")
    parser.add_argument("--resume", action="store_true", default=False,
                        help="Resume from checkpoint: skip already-annotated functions.")
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Show detailed per-step diagnostic output on stderr.")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent.parent

    config_path = project_root / "config" / "agents-config.json"
    if not config_path.exists():
        log(".", AGENT_NAME, f"Error: config not found at {config_path}")
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    project_directory = config.get("project-directory", str(project_root))
    memory_model = config.get("memory-model", "hoare")
    writer_timeout = int(config.get("writer-timeout", 3000))

    input_path = Path(args.in_file)
    output_path = Path(args.out_file)

    if not input_path.exists():
        log(project_directory, AGENT_NAME, f"Error: input file not found: {input_path}")
        sys.exit(1)

    try:
        result = run_splitter(
            input_path=input_path,
            output_path=output_path,
            config_path=config_path,
            project_root=project_root,
            memory_model=memory_model,
            project_directory=project_directory,
            filter_class=args.filter_class,
            filter_func=args.filter_func,
            resume=args.resume,
            verbose=args.verbose,
            writer_timeout=writer_timeout,
        )
    except Exception as e:
        log(project_directory, AGENT_NAME, f"Error: {e}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    log(project_directory, AGENT_NAME, f"Annotated output written to {output_path}")


if __name__ == "__main__":
    main()
