"""pyval-walker-impl.md C1b (driver-backlog item 3, sexp-carrier residual C1b): the
CROSS-CALL extension of the C1 List[str]-accumulator pyval walker. Where 0943's
`walk_path` is self-recursive ONLY, here `walk_outer` CROSS-CALLS a SIBLING walker
`walk_inner` (both `pyval` -> `list string`), the `from_sexp._walk_kername`->
`_walk_modpath` shape. The C1b capability is: (a) a cross-call to a sibling recognized
pyval-list-walker is a legal `listexpr` (resolved via the module-level fixpoint set
`compute_pyval_list_walker_names`), and (b) SCC topological ordering (scc.py, callees
before callers) places `walk_inner`'s `let rec walk_inner` before `walk_outer`, so the
backward reference is in scope — NO `let rec ... with` mutual group is needed because
the call graph is a DAG (no true mutual recursion between the two).

The emitted `walk_outer` body reads the REAL pyval spine — `pystr_eq (…atom (…pnth
v_kn 0)) "KerName"`, the accumulator `…app v_out (walk_inner v_mp)` (the CROSS-CALL),
`…app v_out (Cons (…atom (…pnth v_iid 1)) Nil)` — with NO int-hash, NO oracle. It is a
STRUCTURAL lowering: change any literal / index / the cross-callee and the emitted .mlw
changes (mutation test), so the recognizer is not a facade.

POSITIVE witness (regression lock): both walkers fire `recognize_pyval_list_walker`
(the inner with an empty sibling set, the outer with `{walk_inner}` after the fixpoint),
and the whole file PROVES. If a future edit drops the cross-call resolution or the SCC
ordering, `walk_outer` reverts to a `val` stub (emission byte-diff) and/or the proof
breaks.

No evil-twin applies: the recognizer forces the fixed `ensures True` shape (no
postcondition to refute) and emits NO oracle to collapse to — the mutation test +
`bin/check-emitted-vacuity.py` (0 input-blind) are the non-vacuity lock."""
from typing import Any, List


#@ requires True
#@ ensures True
#@ assigns \nothing
def walk_inner(mp: Any) -> List[str]:
    # A self-recursive (Dot <parent> (Id NAME)) module-path walker (the callee).
    out: List[str] = []
    if not isinstance(mp, tuple):
        return out
    if mp and mp[0] == "Dot":
        if len(mp) >= 3:
            out.extend(walk_inner(mp[1]))
            iid = mp[2]
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                out.append(iid[1])
    return out


#@ requires True
#@ ensures True
#@ assigns \nothing
def walk_outer(kn: Any) -> List[str]:
    # A (KerName <mp> (Id NAME)) walker that CROSS-CALLS the sibling walk_inner.
    out: List[str] = []
    if not isinstance(kn, tuple):
        return out
    if kn and kn[0] == "KerName":
        if len(kn) >= 3:
            mp = kn[1]
            iid = kn[2]
            out.extend(walk_inner(mp))
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                out.append(iid[1])
    return out
