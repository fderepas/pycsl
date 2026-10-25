# OPEN ROUTE #363 — `super(X, self).__init__()` IS CREDITED TO THE DIRECT BASE WHATEVER X IS
**Status: OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r363/`: `r35_super_skip_class.py`, `r42_super_skip_reads_m.py`.

Route #347's constructor-chain summary credits the direct base's `__init__` regardless of X: `super(A, self)` really runs `object.__init__` (r35), `super(M, self)` really runs `A.__init__` (r42); a field read under no_exception proves; CPython AttributeError. (Over-refusal r41 shows the converse.)

Repair: Resolve `super(X, self)` to the class after X in the linearised MRO; refuse when X is not a file class.
