# OPEN ROUTE #437 — sorted() OVER ELEMENTS NOT TOTALLY ORDERED OWES NO TypeError
**Status: OPEN, Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r437/` (10): `oo12_sorted_tuple_str_opt.py`, `x04_sorted_optional.py`, `x05_sorted_tuple_dict.py`, `z03_sorted_tuple_obj.py`, `z04_sorted_tuple_opt.py`, `z06_sorted_tuple_str_dict.py`, `z07_sorted_opt_str.py`, `z09_sorted_tuple_list_dict.py`, `z12_sorted_tuple_dict_rev.py`, `z14_sorted_list_opt.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#437 sorted() OVER ELEMENTS NOT TOTALLY ORDERED OWES NO TypeError   (10)
  z04  xs: List[Tuple[int, Optional[int]]]; sorted(xs) PROVED; [(1, 1), (1, None)]            CPython TypeError
  x04 List[Optional[int]]   x05 / z06 / z09 / z12 tuples ending in a dict (reverse= too)   z03 tuple of a user class without
  __lt__   z07 Optional[str]   z14 list of Optional   oo12 Tuple[str, Optional[int]]
  REPAIR (proposed, allow-list / refuse by default): `sorted(it)` / `list.sort()` / min / max (no key=) are admitted only when the element class is in a totally-ordered
  allow-list (int, bool, str, bytes, float(*), tuples whose every component class is admitted, user classes with a
  verified __lt__); otherwise refused under `no_exception` (TypeError). A key= callable: same rule on its result class.
```
