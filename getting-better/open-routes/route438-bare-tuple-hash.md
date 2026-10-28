# OPEN ROUTE #438 — HASHING A BARE / UNPARAMETERISED tuple (ELEMENTS UNKNOWN) OWES NO TypeError
**Status: OPEN, Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r438/` (11): `u1_ret_tuple_bare.py`, `w00_hash_bare_tuple.py`, `w04_ifexp_bare_tuple.py`, `w05_tuple_in_tuple.py`, `w06_walrus_bare_tuple.py`, `w07_typing_Tuple_ret.py`, `w11_method_bare_tuple.py`, `y00_param_bare_tuple.py`, `y01_param_typing_Tuple.py`, `y13_ret_bare_tuple_local.py`, `y14_field_bare_tuple.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#438 HASHING A BARE / UNPARAMETERISED tuple (ELEMENTS UNKNOWN) OWES NO TypeError   (11)
  w00  t: tuple; hash(t) PROVED; f(([1],))                                                     CPython TypeError
  y00 / y01 {t} for a parameter `tuple` / `typing.Tuple`   u1 / y13 / w07 a callee returning `-> tuple`   w04 IfExp
  w05 a tuple inside a tuple   w06 walrus   w11 method return   y14 a field annotated `tuple`
  REPAIR (proposed, allow-list / refuse by default): The hash allow-list (rh1 / #407) admits a tuple only with every component class admitted; `tuple`, `Tuple`, `tuple[Any, ...]`
  and `Tuple[()]`-less spellings have UNKNOWN components and are #UNK: refused in a hashing position under `no_exception`.
```
