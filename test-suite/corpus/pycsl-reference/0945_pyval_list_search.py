"""pyval-walker-impl.md C1b (driver-backlog item 3, sexp-carrier residual C1b): the
SEARCH catamorphism counterpart of the C1 accumulator walker. Where 0943/0944 BUILD a
`List[str]` via `.append`/`.extend`, this SEARCHES a heterogeneous pyval tree for the
first non-empty per-node reader result, recursing on EVERY element of the spine (the
`from_sexp._find_kername_components` shape). It cannot use the single-`pv_size`-variant
+ `size_nthl` lemma path (the self-call is on a spine ELEMENT, not a direct `p[i]`), so
it emits the certified pyval CATAMORPHISM: a mutual

    let rec find (v: pyval) : list string       variant { pv_size v }
    with find__list (l: list pyval) : list string variant { size_list l }

whose cross-decreasing structural measures discharge termination AUTOMATICALLY — the
`emit_bool_multiway_group` precedent — with NO new axiom (ledger stays 3).

The emitted `find` body reads the REAL pyval spine — the guard
`is_plist v && plen v > 0 && pystr_eq (atom (pnth v 0)) "Leaf"`, the leaf reader
`collect_leaf v` (a sibling accumulator walker CROSS-CALL), the spine search
`match find v_sub with Nil -> false | _ -> true` selecting the first non-empty — with
NO int-hash, NO oracle. It is a STRUCTURAL lowering: change the "Leaf" tag / the reader
/ the guard and the emitted .mlw changes (the mutation test), so it is not a facade.

POSITIVE witness (regression lock): `find` fires `recognize_pyval_list_search`,
`collect_leaf` fires `recognize_pyval_list_walker`, and the whole file PROVES (the
mutual pv_size/size_list termination + the cross-call). If a future edit drops the
search recognition or the mutual-group termination, `find` reverts to a `val` stub
(emission byte-diff) and/or the proof breaks.

No evil-twin applies: the recognizer forces the fixed `ensures True` shape (no
postcondition to refute) and emits NO oracle to collapse to — the mutation test +
`bin/check-emitted-vacuity.py` (0 input-blind) are the non-vacuity lock."""
from typing import Any, List


#@ requires True
#@ ensures True
#@ assigns \nothing
def collect_leaf(node: Any) -> List[str]:
    # The per-node reader: a (Leaf (Id NAME) ...) accumulator walker (the callee
    # the search cross-calls when the guard fires).
    out: List[str] = []
    if not isinstance(node, tuple):
        return out
    if node and node[0] == "Leaf":
        if len(node) >= 2:
            iid = node[1]
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                out.append(iid[1])
    return out


#@ requires True
#@ ensures True
#@ assigns \nothing
def find(payload: Any) -> List[str]:
    # Search the tree for the first Leaf subtree and return its collected names.
    if isinstance(payload, tuple):
        if payload and payload[0] == "Leaf":
            return collect_leaf(payload)
        for sub in payload:
            r = find(sub)
            if r:
                return r
    return []
