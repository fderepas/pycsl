# OPEN ROUTE #279 — LIST ALIASING LOST BY `+=` AND BY CHAINED ASSIGNMENT
**Status: OPEN (gen #37, 2026-10-19), Severity 1.** Red-team round 6; driver-reproduced at 78162575 (rc=0; CPython AssertionError).
Witnesses `witnesses-r279/`. p117: `b = a; b += [1]; len(a)` proves 1 (emits `b := !b ++ ...` on a copy); the
aliased-list-mutation refusal fires for `.append` (p143) but not for `+=` on a list. p216: `a = b = []; b.append(1)`
proves `len(a) == 0` — chained assignment goes through a temp (`a := !_pycsl_multi_1; b := !_pycsl_multi_1`) that
the alias refusal does not see. Repair: treat list `+=` as an in-place mutation for the alias rule, and treat a
chained assignment of a mutable value as an alias binding (refuse or model).
