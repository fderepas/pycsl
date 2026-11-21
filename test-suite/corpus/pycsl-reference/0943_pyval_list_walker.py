"""pyval-walker-impl.md C1 (driver-backlog item 3, sexp-carrier residual C1): the
LIST-accumulator counterpart of the value-returning pyval string walker. Where the
string walker (0942) returns an `Optional[str]`, this returns a `List[str]` BUILT by
`.append` / `.extend` / `reversed` over the certified pyval spine (the `from_sexp`
`_walk_modpath` shape), lowered onto the pyval ADT (PStr=atom, PList=tuple) via inline
TOTAL projectors pv_nth/pv_len/atom_of + inline TOTAL list ops app/rev. Tree
self-recursion terminates via an axiom-free per-function `let rec lemma __size_nthl`
(in-range element size <= list size; the recursion IS the induction, Alt-Ergo-proved,
NO new axiom — ledger stays 3).

The emitted body reads the REAL pyval spine — `pystr_eq (…atom (…pnth v_x 0)) "Id"`,
the accumulator built by `…app …acc (Cons (…atom (…pnth v_x 1)) Nil)`, the tree
self-call `walk_path (…pnth v_x 1)` — with NO int-hash, NO `any_1`/opaque oracle. It
is a STRUCTURAL lowering: change any literal / index / guard and the emitted .mlw
changes (the mutation test), so the recognizer is not a facade.

POSITIVE witness (regression lock): this standalone `walk_path` fires the
`recognize_pyval_list_walker` recognizer and PROVES (the outer tree recursion on
`pv_size`, the inner spine fold on the `list pyval` structural variant). If a future
edit collapses the recognizer to an input-blind oracle, this file's emission changes
(byte-diff) and/or the whole-file proof breaks.

No evil-twin applies: the recognizer forces the fixed `ensures True` shape (no
postcondition to refute) and emits NO oracle to collapse to — the mutation test +
`bin/check-emitted-vacuity.py` (0 input-blind) are the non-vacuity lock."""
from typing import Any, List


#@ requires True
#@ ensures True
#@ assigns \nothing
def walk_path(node: Any) -> List[str]:
    # Walk a nested (Dot <parent> (Id NAME)) tree, collecting the Id names
    # left-to-right; a reversed leaf list exercises `.extend(reversed(...))`.
    out: List[str] = []
    if not isinstance(node, tuple):
        return out
    if node and node[0] == "Leaf":
        if len(node) >= 2:
            segs = node[1]
            rev: List[str] = []
            if isinstance(segs, tuple):
                for seg in segs:
                    if isinstance(seg, tuple) and seg[0] == "Id" and len(seg) >= 2:
                        rev.append(seg[1])
            out.extend(reversed(rev))
    elif node and node[0] == "Dot":
        if len(node) >= 3:
            out.extend(walk_path(node[1]))
            iid = node[2]
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                out.append(iid[1])
    return out
