# OPEN ROUTE #347 — A FIELD STORED ON ONLY SOME `__init__` PATHS IS ASSUMED PRESENT
**Status: OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r347/`: `k03_branch_init_field.py`.

`__init__(self, flag): if flag: self.x = 1`; `f(r)` under `no_exception` returns `r.x` and PROVES; CPython `f(R(False))` raises AttributeError. Route #342 checks store forms only for invariant-carrying classes.

Repair: Refuse (or obligate) a field read under `no_exception` when some constructor path does not store it (definite-assignment over `__init__`).
