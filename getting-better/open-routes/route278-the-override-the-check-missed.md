# OPEN ROUTE #278 — `--check-behavioral-subtyping` IGNORES RAISES AND MRO-INHERITED OVERRIDES
**Status: OPEN (gen #37, 2026-10-19), Severity 1.** Red-team round 6; driver-reproduced at 78162575 WITH the flag (rc=0; CPython ValueError / AssertionError).
Witnesses `witnesses-r278/`. p091: `B.m` raises an undeclared ValueError; `use(a: A)` claims `no_exception \all`
over `a.m()` — the refinement goal compares requires/ensures only (not raises/no_exception), and #272's
undeclared-callee-raise rule resolves `a.m()` by static type A only. p092: `class B(M, A): pass` inherits `m`
from mixin M (returns 2) — override pairs are recorded only for methods DEFINED in the subclass, not for ones
the MRO supplies from another base. Repair: raises refinement (override's raises ⊆ base's declared raises) and
override pairs computed over the MRO-resolved method of every subclass.
