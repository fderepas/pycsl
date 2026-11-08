# OPEN ROUTE #454 — STARRED element of a tuple display over a non-iterable `(*n,)` lowered as `n` (TypeError)
**Status: REPAIRED (executor r3, driver run #3, 2026-10-29), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
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

## REPAIR (executor r3, driver run #3, 2026-10-29, off db6c57253; annotations §7.203, translational §T.6.213)

Code inline in the same block as #452 (`_run_pipeline`; mirror twin `\trusted`; no emission change). Under a
claim covering TypeError, every starred element `*x` of a tuple / list / set display in Load context and of a call's
positional arguments needs every derived class of `x` iterable (#441's `IT` code, or a file class whose MRO binds
`__iter__`; the function's own `*args` is a tuple), and every `**m` (call keyword, dict display) needs `m` derived `dict` /
`Mapping` (`PYCSL-R454-STARRED-NON-ITERABLE`). Starred assignment targets receive a list (their source is #173 / #301's).
Witnesses 7025-7027 (all 3 probes: PROVED at base, REFUSED). Control 7028 (`(*xs, 1)` over `Tuple[int, int]`): PROVED at
base and candidate. Cost: 3 expected-FAIL route-#375 witnesses (5066 / 5071 / 5072, `*self` on a field-less class) go
VERIFY-FAIL -> REFUSED; 0 PASS files.

GATES (one candidate, one battery for #447 / #451 / #452 / #454 / #456 / #459; see the README run-#3 r3 entry): fidelity sync / mirror-check rc=0; root corpus 2569 base -> 2581 candidate .mlw, 0 MOVED, 3 GONE (5066 / 5071 / 5072, expected FAIL route-#375 witnesses `[*self]` / `(*self,)` / `g(*self)` on a field-less class: VERIFY-FAIL -> REFUSED by #454), 0 APPEARED; pyref 2186 / 2186 0 / 0 / 0; mirror 53 / 53 0 / 0 / 0 (no OWED proof); planes / ledgers: see the README entry.

## RESIDUALS: a file class iterable only through `__getitem__` (the old sequence protocol) is refused; an underivable
starred value is refused (over-refusal, measured 0).
