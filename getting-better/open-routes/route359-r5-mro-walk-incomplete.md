# OPEN ROUTE #359 — R5's MRO WALK SEES ONLY TOP-LEVEL `def`s AND SKIPS IMPORTED MRO CLASSES
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r357 executor off 1a9cfa42 — see REPAIR). Was OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r359/`: `m15_rec_assign_override.py`, `m16_rec_lambda_override.py`, `m17_rec_conditional_def.py`, `m19_rec_imported_mixin.py`, `m20_rec_mixin_inherits_import.py`, `m21_rec_try_def.py`.

Route #344's C3 walk finds a method only as a top-level `def` of a file class: `B.m` bound by `m = _bm`, a lambda, a `def` under `if` or `try` (m15/m16/m17/m21) is skipped, so `C.m` resolves to `A.m` and R5 compares it with itself; `a.m() % 1 == 0` proves, CPython 0.5. Imported MRO classes are skipped too (#344 residual), reachable directly (m19) and through a file class `B(Bf)` with no def (m20). Helper `rt26other.py`.

Repair: Treat a class body binding the name by ANY statement (Assign / AnnAssign / def under if/try/with) as defining it and refuse what R5 cannot compare; refuse when a class from outside the file precedes the defining class in the MRO.
