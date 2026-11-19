from typing import Any, Dict, List, Optional, Set, Tuple

PyVal = Any


#@ requires True
#@ ensures True
#@ assigns \nothing
def emits_as_logic_symbol(f: Dict[str, PyVal]) -> bool:
    return False


#@ requires True
#@ ensures True
#@ assigns \nothing
def find_calls_in_ir(n: PyVal, s: Set[str]) -> Set[str]:
    return set()


#@ requires True
#@ ensures True
#@ assigns \nothing
def sort_functions_by_scc(
    functions: List[Dict[str, PyVal]],
    extra_concrete: Optional[Set[str]] = None,
) -> Tuple[List[Dict[str, PyVal]], Dict[str, tuple]]:
    """Return functions in SCC-topological order and a scc_info dict.

    `extra_concrete` (W8 capability (vi)) names further callees that are concrete-called
    from a sibling — the RECORD-returning same-class methods, which lower to
    `(<class>__<m> self)` rather than an abstract val — so they get the same
    callee-before-caller ordering edges. Empty by default → identical ordering."""
    func_names_set = {func["name"] for func in functions}
    func_by_name = {func["name"]: func for func in functions}
    # allocator-frame plan §2.7: only `#@ sibling_concrete` callees are concrete-called
    # from siblings, so only they need callee-before-caller ordering edges.
    sibling_concrete_set = {func["name"] for func in functions
                            if func.get("sibling_concrete")}
    if extra_concrete:
        sibling_concrete_set |= (set(extra_concrete) & func_names_set)
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
        # scc2.md: `#@ uses <lemma>` is an explicit ordering citation — the cited
        # lemma must be emitted before this function so its general `forall …` fact is
        # in scope (a goal can rely on a lemma's fact without NAMING it, so no
        # contract-reference edge would form). Added unconditionally (the target is a
        # lemma, deliberately not a `logic_symbol`); the citation is declared intent.
        uses_edges = set(func.get("uses") or []) & func_names_set
        # allocator-frame plan §2b: concrete intra-class `self.<m>()` calls (resolved to
        # the verified same-file method) are body-level ordering edges too.
        self_call_edges = find_self_method_calls(
            func.get("body"), func.get("self_type", ""), func_names_set,
            sibling_concrete_set)
        call_graph[func["name"]] = (body_edges | (contract_refs & logic_symbols)
                                    | uses_edges | self_call_edges)
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
