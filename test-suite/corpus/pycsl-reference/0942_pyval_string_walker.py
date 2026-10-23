"""pyval-walker-impl.md (driver-backlog item 3): the GENERAL value-returning pyval
string walker — a string-RETURNING catamorphism over a heterogeneous nested-tuple
param (the sertop `from_sexp` s-expression shape), lowered onto the certified pyval
ADT (PStr=atom, PList=tuple) via three inline TOTAL projectors pv_nth/pv_len/atom_of
(axiom-free; the pyval `pv_size` cert already covers measure/termination, ledger 3).

Unlike the bool-existence recognizer family (which returns bool), this returns an
`Optional[str]` BUILT from positional index `t[i]`, string-literal tag dispatch
`t[0] == "..."`, `len(t)` guards, and a `for x in t` fold with EARLY string-return.
The emitted body reads the REAL pyval spine — `pystr_eq (…atom (…pnth v_field 0)) "Id"`
and `Arm_?_0 (…atom (…pnth v_inner 1))` — with NO int-hash, NO `any_1`/opaque oracle,
NO `last_atom` sidestep. It is a STRUCTURAL lowering: change any literal / index / guard
and the emitted .mlw changes (the mutation test), so the recognizer is not a facade.

POSITIVE witness (regression lock): this standalone `first_binder_name` fires the
`recognize_pyval_string_walker` recognizer and PROVES (termination via the structural
`list pyval` variant). If a future edit collapses the recognizer to an input-blind
oracle, this file's emission changes (byte-diff) and/or the whole-file proof breaks.

No evil-twin twin is applicable: the recognizer forces the fixed `ensures True` shape
(no postcondition to refute) and emits NO oracle it could vacuously collapse to — so a
mutation test IS decisive here (there is no int-hash erasure to hide behind, unlike the
`all_1`/`any_1` case of 0938/0939). Non-vacuity is locked by the emitted `pystr_eq`
spine-reads + `bin/check-emitted-vacuity.py` (0 input-blind)."""
from typing import Any, Optional


#@ requires True
#@ ensures True
#@ assigns \nothing
def first_binder_name(node: Any) -> Optional[str]:
    # Walk a nested-tuple binder_annot: find the first ("Id", NAME) field's NAME.
    if not isinstance(node, tuple):
        return None
    for field in node:
        if isinstance(field, tuple) and len(field) >= 2 and field[0] == "Id":
            return field[1]
    return None
