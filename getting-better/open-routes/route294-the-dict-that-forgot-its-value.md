# OPEN ROUTE #294 — AN ANNOTATED dict LOCAL WHOSE FIRST ASSIGNMENT IS NOT A dict LITERAL IS LOWERED TO THE EMPTY MAP
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Found by the ch29 drain; driver-reproduced at 7569ccb7
(false_proof_hval_alias.py, false_proof_hval_alias_dictcopy.py rc=0; CPython True).
Witnesses `witnesses-r294/`: `e: Dict[str, str] = func; return "name" in e` with `ensures \result == False` proves (CPython True);
same with `Dict[str, PyVal]` and `dict(func)`; also confirmed for `Dict[str, List[int]]` and `Dict[str, Dict[str, int]]` (value
type string / seq / nested map / hval / emit_ir; NOT int). Site: `src/pycsl/module6_whyml/statements.py` `_emit_first_assign`
(~79-82): `_empty = self._dv_empty_default(nu); if _empty: val = _empty` replaces the lowered RHS before (and regardless of)
the dict-literal test. Affects ordinary user programs. Repair: use the empty base only when the RHS is a dict literal (or
{}); otherwise keep the lowered value (type-checks or fails L3-tc); census every annotated-collection first-assign path.
