# OPEN ROUTE #377 — A NAME BOUND TWICE IN A CLASS BODY: pycsl USES THE FIRST `def`, CPython RUNS THE LAST
**Status: OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r377/`: `a50_init_defined_twice.py`, `a58_method_twice_caller.py`, `a62_init_twice_invariant_param.py`.

The constructor goal and call-site contracts are taken from the first `def` of a name in a class body; CPython keeps the last binding. a50: goal `n = 7 -> n >= 5` from a dead `__init__` (CPython 0); a62: a dead `__init__`'s `#@ requires x >= 0` becomes the goal premise (CPython -3); a58: `c.get()` uses the first def's `ensures result = 1` while the emitted body is the last def (CPython 2). Route #118's duplicate-def check covers module scope only (module-level a57 FAILs correctly).

Repair: Extend #118 to class scopes: refuse a name bound twice in a class body (or resolve the last binding everywhere).
