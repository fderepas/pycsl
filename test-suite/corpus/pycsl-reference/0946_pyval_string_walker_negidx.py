"""pyval-walker-impl.md C2 (driver-backlog item 3, from_sexp residual C2): the
NEGATIVE-index-from-end + Optional[str]-return extension of the value-returning
pyval STRING walker (0942). Where 0942's `_binder_name` is a self-contained
Optional[str] fold, here `short_name` (the `from_sexp._const_name`/`_ind_short_name`
shape) (a) binds a `list string` local from a CROSS-CALL to a sibling
pyval->`list string` SEARCH walker `find_components`, then (b) returns
`parts[-1] if parts else None` — a NEGATIVE index from the END of that list, inside
a conditional-expression that composes with the synthesized Optional[str] union.

The C2 capability is three composed features, all in the string-walker recognizer/
emitter (`generic_fold.py`):
  - a `<var> = <sibling>(vref)` assign binds `var` as a `list string` local
    (tracked in `slist`, resolved via the module-level pyval-list-walker fixpoint
    `compute_pyval_list_walker_names`; SCC ordering places the sibling first);
  - `<var>[-k] if <var> else None` (an `IfExpr` return) lowers to a real
    if/then/else over the union arms, with the truthiness `<var>` -> `lens var > 0`;
  - `<var>[-k]` (k>=1) lowers to `nths var (lens var - k)` via two inline TOTAL
    `list string` projectors (nths/lens, DEFINED not axiomatized; the projectors are
    total — return "" past the end — so NO unsound OOB assumption is made, and the
    `if var` guard keeps the real read in range). Ledger stays 3.

The emitted `short_name` body reads the REAL structure — `is_plist`, `plen`, the
CROSS-CALL `(find_components (pnth v_node 1))`, `lens v_parts > 0`, and
`nths v_parts (lens v_parts - 1)` — with NO int-hash, NO oracle, NO any_1. It is a
STRUCTURAL lowering: the neg-index OFFSET tracks k (`[-1]` -> `- 1`, `[-2]` ->
`- 2`), so changing the index / the literal / the cross-callee changes the emitted
.mlw (the decisive mutation test). See 0947 for the `[-2]` discriminating twin.

POSITIVE witness (regression lock): `find_components` fires the list SEARCH
recognizer and `short_name` fires the extended STRING walker; the whole file PROVES.
A regression that drops the cross-call binding, the neg-index offset, or the
Optional composition reverts `short_name` to a `val` stub (emission byte-diff) and/or
breaks the proof.

No evil-twin applies: the recognizer forces the fixed `ensures True` shape (no
postcondition to refute) and emits NO oracle to collapse to — the mutation test +
`bin/check-emitted-vacuity.py` (0 input-blind) are the non-vacuity lock."""
from typing import Any, List, Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def find_components(payload: Any) -> List[str]:
    # A pyval-tree SEARCH walker (the `_find_kername_components` shape): return the
    # first non-empty per-node reader result, recursing on every spine element.
    if isinstance(payload, tuple):
        if payload and payload[0] == "Leaf":
            return leaf_components(payload)
        for sub in payload:
            r = find_components(sub)
            if r:
                return r
    return []


#@ requires True
#@ ensures True
#@ assigns \nothing
def leaf_components(kn: Any) -> List[str]:
    # A self-contained accumulator walker feeding the search (the callee's callee).
    out: List[str] = []
    if not isinstance(kn, tuple):
        return out
    if kn and kn[0] == "Leaf":
        for seg in kn:
            if isinstance(seg, tuple) and seg[0] == "Id" and len(seg) >= 2:
                out.append(seg[1])
    return out


#@ requires True
#@ ensures True
#@ assigns \nothing
def short_name(node: Any) -> Optional[str]:
    # The C2 shape: guard, bind a `list string` from the sibling search walker,
    # then return the LAST element (negative index from end) or None.
    if not isinstance(node, tuple) or len(node) < 2:
        return None
    parts = find_components(node[1])
    return parts[-1] if parts else None
