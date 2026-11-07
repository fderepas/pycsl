# OPEN ROUTE #412 — FLOAT TRUE DIVISION HAS NO DIVISION-BY-ZERO OBLIGATION
**Status: REPAIRED (candidate, g2 run #3), Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r412/`: `i02_float_div_zero.py`, `j13_float_div_literal.py`, `j12_float_inverse.py`.

```
#412 FLOAT TRUE DIVISION HAS NO DIVISION-BY-ZERO OBLIGATION  [old family]
  i02  x / y (x, y: float) under no_exception PROVED                                            ZeroDivisionError
  j13  x / 0.0;   j12  1.0 / (x - x)                                                           ZeroDivisionError
  WhyML: `val function float_div_op (a b: real) : real`, no requires. (float // and %, x / n with an int n, n / y
  with a float y, sum(xs) / len(xs) are refused -- j02, j03, j10, j11, j14.)
  REPAIR: `requires { b <> 0.0 }` on float_div_op (the int-int path pycsl_div already has it).
```

## REPAIR (2026-10-26, g2 executor off 4431ef86f; docs annotations §7.70 / translational §T.6.81)
**An obligation, exactly as for int division.** In a body under a `no_exception` covering ZeroDivisionError (the existing
`("binop", "/")` trigger row decides), float `x / y` lowers to `(float_div_op x (begin assert { y <> 0.0 }; y end))`, and
int TRUE division `a / b` -- found during the repair to be the one int division path the row never wrapped (`a / b` with
no `b != 0` PROVED `no_exception \all`, new witness 6059) -- to `(float_truediv_op a (begin assert { no_div_zero (b) }; b
end))`. The obligation wraps the right OPERAND so the term keeps its head (`_STRING_VALUED_OPS`-style prefix checks).
Spec context and functions without `no_exception` are unchanged. Live `_handle_binop` only (mirror twin `\trusted`).
Measured together on the final candidate (g2 worktree off 4431ef86f; base = the official `bin/byte-diff-sweep.sh` at 4431ef86f
from the clean g1-base tree, cwd = tree root; candidate the same script from the g2 tree): root 2441 -> 2455 .mlw, 2 MOVED
(`1163`, `1164`: #414's shift obligation), 1 GONE (`3269`, #415), 0 APPEARED, 15 new emitting sources (the 20 new witnesses /
controls minus the 5 refused); pyref 2186 -> 2186, 1 MOVED (`0110`: #412's `no_div_zero (0)` inside a `try/except
ZeroDivisionError`, exactly the assert `//` already gets there), 0 GONE, 0 APPEARED; mirrors 53/53, 0 MOVED / 0 GONE / 0
APPEARED. M1 re-proofs base -> candidate: `1163` FAIL -> FAIL (expected FAIL), `1164` PROVED -> PROVED, `3269` FAIL -> REFUSED
(expected FAIL), pyref `0110` FAIL -> FAIL (a pre-existing real/int type error at both).
Movers of this route alone: pyref `0110` (above). Over-refusal: none (no refusal is added).
Witnesses (PROVED rc=0 at base -> FAIL rc=1): 6056 (i02), 6057 (j13), 6058 (j12), 6059 (int `a / b`, no `b != 0`).
Control 6060 (float `/` under `requires y != 0.0` / `x > 0.0`, bounded int `a / b`): PROVED at base and candidate.
Residual: none known for `/`; float `//` / `%` / mixed int-float `/` stay refused as before (j02-j14).
