# OPEN ROUTE #413 — INT TRUE DIVISION a / b HAS NO OVERFLOW OBLIGATION
**Status: REPAIRED (candidate, g2 run #3), Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r413/`: `i01_true_div_overflow.py`.

```
#413 INT TRUE DIVISION a / b HAS NO OVERFLOW OBLIGATION  [old family; arguably FLOAT-FINITE]
  i01  requires b != 0; a / b; f(10**400, 1)                                                   OverflowError
  WhyML: `val function float_truediv_op (a b: int) : real`. REPAIR: obligation |a / b| < 2**1024 (or require
  |a| < 2**1024 when |b| >= 1), or list the site under FLOAT-FINITE's `relied_on_by` explicitly.
```

## REPAIR (2026-10-26, g2 executor off 4431ef86f; docs annotations §7.71 / translational §T.6.82)
**Decision: FLOAT-FINITE does NOT cover it** -- the declared assumption is a claim about float VALUES (finite, non-NaN:
`x == x`), not that no OverflowError is raised; listing the site under its `relied_on_by` would have widened a declared
assumption (a user decision), so an OBLIGATION was added instead. OverflowError is not a Phase 1 exception, so, like
AssertionError (route #332, §7.19), it is owed under `no_exception \all` only: int `a / b` owes
`(- M * b <= a <= M * b) \/ (M * b <= a <= - M * b)` with M = DBL_MAX = (2**53 - 1) * 2**971 as a decimal literal, i.e.
|a| <= M |b|, so |a / b| <= DBL_MAX and CPython's correctly rounded quotient is finite (measured: `(2**1024 - 2**970 - 1) / 1`
is fine, `(2**1024 - 2**970) / 1` overflows; the obligation is slightly conservative only between DBL_MAX and that
rounding boundary). Linear in `a`, `b`. In the same right-operand block as #412's `no_div_zero`.
Measured together on the final candidate (g2 worktree off 4431ef86f; base = the official `bin/byte-diff-sweep.sh` at 4431ef86f
from the clean g1-base tree, cwd = tree root; candidate the same script from the g2 tree): root 2441 -> 2455 .mlw, 2 MOVED
(`1163`, `1164`: #414's shift obligation), 1 GONE (`3269`, #415), 0 APPEARED, 15 new emitting sources (the 20 new witnesses /
controls minus the 5 refused); pyref 2186 -> 2186, 1 MOVED (`0110`: #412's `no_div_zero (0)` inside a `try/except
ZeroDivisionError`, exactly the assert `//` already gets there), 0 GONE, 0 APPEARED; mirrors 53/53, 0 MOVED / 0 GONE / 0
APPEARED. M1 re-proofs base -> candidate: `1163` FAIL -> FAIL (expected FAIL), `1164` PROVED -> PROVED, `3269` FAIL -> REFUSED
(expected FAIL), pyref `0110` FAIL -> FAIL (a pre-existing real/int type error at both).
Movers of this route alone: none. Over-refusal: none.
Witness 6061 (i01) PROVED rc=0 at base -> FAIL rc=1. Control 6062 (`|a| <= 10**300`, `b != 0`; `a / 3` with `|a| <= 10**308`):
PROVED at base and candidate.
Residual (not a witness of this route, not repaired): `float(n)` / an int-to-float conversion of a huge int
(`int too large to convert to float`) is a sibling OverflowError site, not measured here.
