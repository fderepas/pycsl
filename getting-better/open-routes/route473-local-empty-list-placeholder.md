# OPEN ROUTE #473 — A LOCAL EMPTY LIST PASSED TO A CALLEE IS THE 1024-ELEMENT PLACEHOLDER (discharges `len(c) >= 1`)
**Status: OPEN, Severity 1.** Found by executor lv5 (driver run #3, 2026-10-29) while building a conversion control;
driver-reproduced on main a9eac4a08 (`scratchpad/rt38/driver-repro-r473.txt`): `c = []` and `c: List[int] = []` then
`g(c)` with `g` requiring `len(c) >= 1` PROVE (rc=0 Verification SUCCESS); CPython IndexError. (`c = list()` already FAILS.)
Witnesses `witnesses-r473/` (2): `r473_local_empty_list_to_callee.py`, `r473b_annotated_empty_list.py`.

```
#473 `c = []; return g(c)` is emitted `let c = (Array.make 1024 0) in g c`: the empty-list PLACEHOLDER (routes #195 /
     #196 / #225 family; #195 / #196 closed only the DIRECT `f([])` argument form). Inside the function `len(c)` is tracked
     locally (a control `n = len(c)` with `ensures \result == 1024` does not prove), but the ARRAY handed across the call is
     the 1024-element placeholder, so the callee's length precondition is discharged against 1024.
  REPAIR (proposed, structural): an empty list literal must never be materialised as a fixed-size placeholder where it
  can reach a callee / a field / a return / a container: either emit a length-0 array (or the resizable-list model) or
  refuse passing such a value across a boundary; census every `Array.make 1024` placeholder site.
```
