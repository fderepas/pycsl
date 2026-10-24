# OPEN ROUTE #344 — AN OVERRIDE INHERITED THROUGH THE MRO (MULTIPLE INHERITANCE) ESCAPES R5
**Status: OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r344/`: `c01_mi_override_float.py`.

`class C(B, A)` with no own `m`; `A.m -> int`, `B.m -> float` returning 0.5. pycsl records `c__m refines a__m` and emits `c__m : real`, but R5 (route #338) reads the two defs from source and C has none, so the return annotation is never compared: `g(a: A)` with `ensures a.m() % 1 == 0` PROVES; CPython `g(C())` is 0.5. Contract-level MI variants (c02, j10, j11) FAIL correctly.

Repair: Run R5 over every recorded refinement pair, resolving the inherited def through the C3 MRO.
