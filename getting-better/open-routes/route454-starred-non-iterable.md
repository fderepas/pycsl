# OPEN ROUTE #454 — STARRED element of a tuple display over a non-iterable `(*n,)` lowered as `n` (TypeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r454/` (3): `c14_u002.py`, `c17_z000.py`, `c17_z009.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F11 -- STARRED element of a tuple display over a non-iterable `(*n,)` lowered as `n` (TypeError)   (3)
  EXEMPLAR c17/z000.py  PROVED (rc=0 Verification SUCCESS):
    | class P:
    |     def __init__(self, x: int) -> None:
    |         self.x = x
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(n: int) -> int:
    |     return len((*n,))
    CPython 3.14: f(1)  ->  VIOLATION TypeError Value after * must be an iterable, not int
  MECHANISM: A starred element in a TUPLE display over a non-iterable (`(*n,)`, `(*b,)` with n: int, b: bool) lowers to `n`
  itself (`iter_length (n)`, mlw/z000): no iterability check. List / set displays with the same element are refused
  (#438) or do not type-check.
  REPAIR: OBLIGATION: a starred display element must be DERIVED iterable (#441's IT code) -- the same check `list(x)` gets
  -- in tuple, list and set displays alike; refuse otherwise (TypeError).
  MEMBERS: c14/u002.py c17/z000.py c17/z009.py
```
