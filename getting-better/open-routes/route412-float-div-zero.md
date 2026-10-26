# OPEN ROUTE #412 — FLOAT TRUE DIVISION HAS NO DIVISION-BY-ZERO OBLIGATION
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r412/`: `i02_float_div_zero.py`, `j13_float_div_literal.py`, `j12_float_inverse.py`.

```
#412 FLOAT TRUE DIVISION HAS NO DIVISION-BY-ZERO OBLIGATION  [old family]
  i02  x / y (x, y: float) under no_exception PROVED                                            ZeroDivisionError
  j13  x / 0.0;   j12  1.0 / (x - x)                                                           ZeroDivisionError
  WhyML: `val function float_div_op (a b: real) : real`, no requires. (float // and %, x / n with an int n, n / y
  with a float y, sum(xs) / len(xs) are refused -- j02, j03, j10, j11, j14.)
  REPAIR: `requires { b <> 0.0 }` on float_div_op (the int-int path pycsl_div already has it).
```
