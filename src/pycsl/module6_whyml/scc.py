from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple


def find_calls_in_ir(obj: Any, func_names_set: Set[str]) -> Set[str]:
    """Find all function names called within an IR object."""
    calls: Set[str] = set()
    if isinstance(obj, dict):
        if obj.get("type") == "Call" and obj.get("func") in func_names_set:
            calls.add(obj["func"])
        for v in obj.values():
            calls |= find_calls_in_ir(v, func_names_set)
    elif isinstance(obj, list):
        for item in obj:
            calls |= find_calls_in_ir(item, func_names_set)
    return calls


def compute_sccs(names: Set[str], call_graph: Dict[str, Set[str]]) -> List[List[str]]:
    """Compute SCCs via Tarjan's algorithm. Returns SCCs in topological order
    (callees before callers). Each SCC is a list of function names."""
    index_counter = [0]
    stack: List[str] = []
    lowlink: Dict[str, int] = {}
    index: Dict[str, int] = {}
    on_stack: Dict[str, bool] = {}
    sccs: List[List[str]] = []

    def strongconnect(v: str) -> None:
        index[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True
        for w in call_graph.get(v, set()):
            if w not in names:
                continue
            if w not in index:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w):
                lowlink[v] = min(lowlink[v], index[w])
        if lowlink[v] == index[v]:
            scc: List[str] = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in sorted(names):  # sorted for determinism
        if v not in index:
            strongconnect(v)

    # Tarjan's outputs callees before callers — already the order we want
    return sccs


def sort_functions_by_scc(
    functions: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, tuple]]:
    """Return functions in SCC-topological order and a scc_info dict."""
    func_names_set = {func["name"] for func in functions}
    func_by_name = {func["name"]: func for func in functions}
    call_graph: Dict[str, Set[str]] = {}
    n = len(functions)
    i = 0
    while i < n:
        func = functions[i]
        call_graph[func["name"]] = (
            find_calls_in_ir(func["body"], func_names_set) & func_names_set
        )
        i += 1
    ordered_sccs = compute_sccs(func_names_set, call_graph)
    sorted_names = [name for scc in ordered_sccs for name in scc]
    scc_info: Dict[str, tuple] = {}
    for scc_idx, scc in enumerate(ordered_sccs):
        scc_size = len(scc)
        for pos, name in enumerate(scc):
            scc_info[name] = (scc_idx, pos, scc_size)
    for func in functions:
        if func["name"] not in sorted_names:
            sorted_names.append(func["name"])
            scc_info[func["name"]] = (len(ordered_sccs), 0, 1)
    return [func_by_name[name] for name in sorted_names], scc_info
