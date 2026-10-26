# OPEN ROUTE #413 — INT TRUE DIVISION a / b HAS NO OVERFLOW OBLIGATION
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r413/`: `i01_true_div_overflow.py`.

```
#413 INT TRUE DIVISION a / b HAS NO OVERFLOW OBLIGATION  [old family; arguably FLOAT-FINITE]
  i01  requires b != 0; a / b; f(10**400, 1)                                                   OverflowError
  WhyML: `val function float_truediv_op (a b: int) : real`. REPAIR: obligation |a / b| < 2**1024 (or require
  |a| < 2**1024 when |b| >= 1), or list the site under FLOAT-FINITE's `relied_on_by` explicitly.
```
