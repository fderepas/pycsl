import ast
import re
import json
import textwrap
from dataclasses import dataclass, field
from typing import Optional

__all__ = [
    'FunctionInfo',
    '_qualified_name',
    '_extract_functions',
    '_make_func_info',
    '_build_call_graph',
    '_tarjan_scc',
]

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

