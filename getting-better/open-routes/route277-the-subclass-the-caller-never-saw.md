# OPEN ROUTE #277 — A USER-CLASS-TYPED VALUE IS ASSUMED EXACT (override refinement is opt-in only)
**Status: OPEN (gen #37, 2026-10-19), Severity 1.** Red-team round 6; driver-reproduced at 78162575 (rc=0; CPython AssertionError).
Witnesses `witnesses-r277/` (p039 local subclass; p260 base+caller in imported module `rt6lib/base.py`, subclass local).
`use(a: A)` proves `\result == 1` over `a.m()` while `B(A).m` returns 2. The refinement goal exists only under
`--check-behavioral-subtyping` (which catches both), and `--soundness-report` lists NO assumption for this:
it is the user-class twin of BUILTIN-EXACT, undeclared. Repair options: (A) refinement check on by default
(measure corpus cost), or (B) declare a model assumption (e.g. CLASS-EXACT) in `--soundness-report` with
relied_on_by = every method call on a user-class-typed receiver whose class has (or may have) subclasses, plus docs.
