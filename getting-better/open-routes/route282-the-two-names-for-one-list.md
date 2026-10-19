# OPEN ROUTE #282 — DISTINCT PARAMETERS (AND DISTINCT LIST ELEMENTS) ARE ASSUMED NOT TO ALIAS, UNDECLARED
**Status: OPEN (gen #37, 2026-10-19), Severity 2.** Red-team round 6 (found by the r279 executor's census); probes rc=0 at 15953960, CPython violates.
Witnesses `witnesses-r282/`: p111 `f(xs, ys)` with `assigns xs[0]` proves `ys[0] == \old(ys[0])`; caller `f(a, a)` breaks it.
p112 the same through two object parameters; p114 `[r, r]` (one object twice in a list). Every caller that BUILDS the alias in
VERIFIED code is refused (route #254, R167 #243/#244); the residue is an alias built in UNVERIFIED code — ownership rule R1,
exactly like FIELD-DISJOINT (#256) for fields, but NOT listed by `--soundness-report`. Repair: declare it (e.g. PARAM-DISJOINT:
relied_on_by = every function that writes one mutable parameter/element while reading another of a compatible type), docs
in README / static-semantics / translational references, FIELD-DISJOINT precedent; or an opt-in strict mode if cheap.
