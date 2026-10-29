# OPEN ROUTE #448 — builtin row ARITY x KEYWORD cross-constraint: `max/min(a, b, ..., default=)` (TypeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r448/` (6): `c11_q080_realistic_max_default.py`, `c11_q081_min_default_three_ensures.py`, `c3_b002_max_default_multi.py`, `c3_b003_min_default_multi.py`, `c5_k000.py`, `c5_k003.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F5 -- builtin row ARITY x KEYWORD cross-constraint: `max/min(a, b, ..., default=)` (TypeError)   (6)
  EXEMPLAR c11/q080_realistic_max_default.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(a: int, b: int) -> int:
    |     return max(a, b, default=0)
    CPython 3.14: f(3, 4)  ->  VIOLATION TypeError Cannot specify a default for max() with multiple positional arguments
  MECHANISM: #441's max / min row is (1, unbounded, {key, default}) and checks each keyword independently; CPython forbids
  `default=` when more than one positional argument is given. `max(a, b, default=0)` lowers to `MinMax.max a b`.
  REPAIR: Row-level CROSS-CONSTRAINTS in the signature table: a row may carry predicates over (n positional, keyword set);
  max/min: `default` in kw => n_pos == 1. Audit every row for such constraints (sum start vs 2nd positional,
  int base with a non-str first argument, enumerate start duplicate) -- measured: the duplicate forms are refused by
  #275 / #314 today, only max/min default slipped.
  MEMBERS: c11/q080_realistic_max_default.py c11/q081_min_default_three_ensures.py c3/b002_max_default_multi.py c3/b003_min_default_multi.py c5/k000.py c5/k003.py
```
