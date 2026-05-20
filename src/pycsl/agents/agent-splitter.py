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
) -> str:
    """Call agent-writer.py as a subprocess to annotate a single function."""
    cmd = [
        sys.executable,
        str(writer_script),
        "--memory-model", memory_model,
        "--config", str(config_path),
    ]

    # Pass data via stdin as JSON
    input_data = json.dumps({
        "function_source": function_source,
        "callee_contracts": callee_contracts,
        "class_context": class_context,
    })

    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
        cwd=str(project_root),
        timeout=300,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"agent-writer failed (exit {result.returncode}): {result.stderr[:500]}"
        )

    return result.stdout


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


def _body_preserved(original_source: str, annotated_source: str) -> bool:
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
# Main orchestration
# ---------------------------------------------------------------------------

def run_splitter(
    input_path: Path,
    output_path: Path,
    config_path: Path,
    project_root: Path,
    memory_model: str = "hoare",
    project_directory: str = ".",
) -> str:
    """Run the full split-annotate pipeline and return the annotated source."""
    writer_script = Path(__file__).parent / "agent-writer.py"

    source = input_path.read_text(encoding="utf-8")
    log(project_directory, AGENT_NAME, f"Parsing {input_path} ({len(source)} chars)")

    # Step 1: Extract functions and build call graph
    functions, func_map = _extract_functions(source)
    _build_call_graph(functions, func_map)

    log(project_directory, AGENT_NAME,
        f"Found {len(functions)} functions/methods, "
        f"call graph edges: {sum(len(f.callees) for f in functions)}")

    # Filter out dunders and properties (Module5 skips them)
    annotatable = [f for f in functions if not f.is_dunder and not f.is_property]
    annotatable_map = {f.name: f for f in annotatable}

    if not annotatable:
        log(project_directory, AGENT_NAME, "No annotatable functions found, returning original")
        return source

    # Step 2b: Generate class invariants BEFORE annotating methods.
    # Methods need to see the invariant to generate proper guarding `requires`.
    class_invariants = _generate_class_invariants(
        source, functions, {},  # no annotated contracts yet
        memory_model, config_path, project_root, writer_script,
        project_directory,
    )

    # Step 3: Detect SCCs and topological order
    sccs = _tarjan_scc(annotatable_map)
    log(project_directory, AGENT_NAME,
        f"Topological order: {len(sccs)} groups "
        f"(SCCs with >1 member: {sum(1 for s in sccs if len(s) > 1)})")

    # Step 4: Annotate in topological order (leaves first)
    annotated_contracts: dict[str, str] = {}  # qname -> contract text

    for scc in sccs:
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

        if len(scc_funcs) == 1:
            info = scc_funcs[0]
            log(project_directory, AGENT_NAME, f"Annotating: {info.name}")

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
                annotated = _invoke_writer(
                    function_source=info.source,
                    callee_contracts=callee_contracts,
                    class_context=class_ctx,
                    memory_model=memory_model,
                    config_path=config_path,
                    project_root=project_root,
                    writer_script=writer_script,
                )
                annotated = annotated.strip()
                if not annotated:
                    raise RuntimeError("Empty response from writer")
                if not _body_preserved(info.source, annotated):
                    log(project_directory, AGENT_NAME,
                        f"Body stripped for {info.name}, using safe fallback")
                    raise RuntimeError("Body was stripped by LLM")
                info.annotated_source = annotated
                info.contracts = _extract_contracts_text(annotated)
                annotated_contracts[info.name] = info.contracts
            except Exception as e:
                log(project_directory, AGENT_NAME,
                    f"Writer failed for {info.name}: {e}, using safe fallback")
                info.annotated_source = _safe_fallback_annotation(info)
                info.contracts = _extract_contracts_text(info.annotated_source)
                annotated_contracts[info.name] = info.contracts

        elif len(scc_funcs) <= 3:
            # Small mutual recursion group — send all together
            log(project_directory, AGENT_NAME,
                f"Annotating SCC group: {[f.name for f in scc_funcs]}")
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
                annotated = _invoke_writer(
                    function_source=combined_source,
                    callee_contracts=callee_contracts,
                    class_context=class_ctx,
                    memory_model=memory_model,
                    config_path=config_path,
                    project_root=project_root,
                    writer_script=writer_script,
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
                        else:
                            info.annotated_source = func_annotated
                        info.contracts = _extract_contracts_text(info.annotated_source)
                        annotated_contracts[info.name] = info.contracts
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
            # Large SCC — too complex, use safe fallback
            log(project_directory, AGENT_NAME,
                f"Large SCC ({len(scc_funcs)} functions), using safe fallback: "
                f"{[f.name for f in scc_funcs]}")
            for info in scc_funcs:
                info.annotated_source = _safe_fallback_annotation(info)
                info.contracts = _extract_contracts_text(info.annotated_source)
                annotated_contracts[info.name] = info.contracts

    # Step 5: Reassemble the file
    result = _reassemble_file(source, annotatable, class_invariants)
    log(project_directory, AGENT_NAME, "File reassembly complete")
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
        )
    except Exception as e:
        log(project_directory, AGENT_NAME, f"Error: {e}")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    log(project_directory, AGENT_NAME, f"Annotated output written to {output_path}")


if __name__ == "__main__":
    main()
