# OPEN ROUTE #329 — THE `is` REFUSALS (#42, #52) ARE SKIPPED IN AN IF-EXPRESSION TEST AND UNDER `not`
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r329/`: `x = 1; return 7 if x is True else 0` emits `if (!x = 1)` and proves 7 (b31); `if not (x is True): return 0` (b26, #42's
own exploit wrapped in `not`); int-parameter variants (b41, b42); #52's runtime-built string `b is c` inside an if-expression (b43). The refusal sits in
_expr_to_whyml (expressions.py ~21239) keyed on the `py_is` marker; conditions lowered by the if-expression-test / `not` path never reach it.
Plain `if x is True:`, `return x is True`, `bool(x is True)`, `(x is True) == True`, `x is not True` are refused.
Repair: apply the refusal at every condition-lowering path (if-expression test, not, while/if tests, comprehension filters, assert, boolean
operators) — ideally at the IR level for every Compare with `is`/`is not` whose operands are not None/sentinel-safe.
