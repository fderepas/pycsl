# OPEN ROUTE #350 — A PARAMETER DEFAULT THAT CONTRADICTS ITS ANNOTATION IS NOT CHECKED
**Status: OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r350/`: `n06_default_float_for_int.py`, `n07_default_none_for_str.py`.

`def f(x: int = 0.5)` PROVES `ensures x % 1 == 0` (CPython `f()` = 0.5); `def f(s: str = None)` PROVES `len(s)` under `no_exception` (CPython TypeError). The body is verified for the annotation while the default is outside it.

Repair: Require each default to type-check against its annotation (literal kind check, or a precondition obligation at the default), else refuse.
