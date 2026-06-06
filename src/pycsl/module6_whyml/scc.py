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


def emits_as_logic_symbol(func: Dict[str, Any]) -> bool:
    """The SINGLE shared "is this a logic symbol" classifier (scc.md). A function
    whose contract reference forces WhyML declaration order is one that lowers to a
    real `let [rec] function`, so a `(f args)` term in a contract needs `f` declared
    first. Both the SCC edge collector (below) and the emitter's `can_emit_as_logic`
    (`functions.py`) consume this, so "depends on" means the same thing in the graph
    and at emission — the ordering bug existed because they used different notions.

    The emitter additionally requires `not local_refs` (an emission-time term not
    available here); a contract reference to a pure-but-local-ref'd function is
    ill-formed anyway (Why3 rejects a program function in a logic position), so
    omitting that term here only ever over-approximates harmlessly. Lemmas are
    excluded — a `let lemma` is not a term usable in a contract."""
    return (bool(func.get("pure"))
            and func.get("kind") != "method"
            and not func.get("lemma"))


def sort_functions_by_scc(
    functions: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, tuple]]:
    """Return functions in SCC-topological order and a scc_info dict."""
    func_names_set = {func["name"] for func in functions}
    func_by_name = {func["name"]: func for func in functions}
    # scc.md: the only targets a contract reference may edge to are logic symbols.
    logic_symbols = {f["name"] for f in functions if emits_as_logic_symbol(f)}
    call_graph: Dict[str, Set[str]] = {}
    n = len(functions)
    i = 0
    while i < n:
        func = functions[i]
        body_edges = find_calls_in_ir(func["body"], func_names_set) & func_names_set
        # Contract-reference edges (scc.md): a logic symbol named anywhere in this
        # function's contract must be declared before it — `let f … ensures { g x }`
        # is exactly as unbound-symbol-broken as a body call to `g`. Collected with
        # the same `find_calls_in_ir` (it gathers `Call` nodes only, so quantifier /
        # match binders — which are `Var`s — never manufacture phantom edges).
        # Restricted to `logic_symbols`: an impure / method / non-logic reference
        # lowers to an abstract `val` (no declaration-order dependency), so it gets no
        # edge — adding one could fabricate a spurious cycle and mis-group emission.
        # The contract lives under `func["contracts"]` (requires/ensures/assigns/
        # raises); `function_variants` is a sibling top-level key.
        contract_refs: Set[str] = set()
        for _key in ("contracts", "function_variants"):
            contract_refs |= find_calls_in_ir(func.get(_key), func_names_set)
        call_graph[func["name"]] = body_edges | (contract_refs & logic_symbols)
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
