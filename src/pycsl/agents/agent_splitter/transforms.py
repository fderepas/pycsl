import ast
import re
import json
import textwrap
from dataclasses import dataclass, field
from typing import Optional
from agent_splitter.callgraph import *

__all__ = [
    '_extract_contracts_text',
    '_extract_class_context',
    '_fix_annotation_indentation',
    '_reassemble_file',
    '_body_preserved',
    '_graft_contracts',
    '_safe_fallback_annotation',
    '_compute_assigns_hint',
    '_format_assigns_hint',
    '_split_annotated_functions',
]

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


def _graft_contracts(original: str, annotated: str) -> str:
    """Extract #@ contract lines from LLM output and graft onto the original body.

    When the LLM modifies the function body (failing _body_preserved), we can
    still salvage its contract work by extracting the #@ lines and prepending
    them to the original, untouched function source.

    Returns the original function with LLM-generated contracts prepended before
    the def line, or empty string if no contracts were found.
    """
    # Extract #@ lines from the annotated output (only those before the def line)
    contract_lines = []
    for line in annotated.splitlines():
        stripped = line.strip()
        if stripped.startswith("#@"):
            contract_lines.append(stripped)
        elif re.match(r'\s*def\s+', line):
            break

    if not contract_lines:
        return ""

    # Find the def line in the original to get the correct indentation
    orig_lines = original.splitlines(keepends=True)
    indent = ""
    def_idx = -1
    for i, line in enumerate(orig_lines):
        m = re.match(r'^(\s*)def\s+', line)
        if m:
            indent = m.group(1)
            def_idx = i
            break

    if def_idx < 0:
        return ""

    # Build the contract block with correct indentation
    contract_block = "".join(f"{indent}{cl}\n" for cl in contract_lines)

    # Insert before the def line
    result_lines = list(orig_lines)
    result_lines.insert(def_idx, contract_block)
    return "".join(result_lines)


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

