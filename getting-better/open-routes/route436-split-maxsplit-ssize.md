# OPEN ROUTE #436 — str.split / rsplit WITH maxsplit OUTSIDE C ssize_t OWES NO OverflowError
**Status: OPEN, Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r436/` (5): `m04_split_maxsplit.py`, `t0_split_param.py`, `t4_split_neg_ok.py`, `t7_split_ens.py`, `t9_split_loop.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#436 str.split / rsplit WITH maxsplit OUTSIDE C ssize_t OWES NO OverflowError   (5)
  t0   s.split(" ", n) PROVED; n = 10**20                                                      CPython OverflowError
  m04 maxsplit= keyword   t4 negative huge   t7 ensures-bearing   t9 in a loop
  REPAIR (proposed, allow-list / refuse by default): An int-read `maxsplit` (positional or keyword) of split / rsplit / splitlines-like C-ssize_t parameters owes
  `-2**63 <= n < 2**63` under `\all`; enumerate the other ssize_t-parameter methods (str.replace count, expandtabs, ..)
  and either add the obligation or refuse a non-literal argument.
```
