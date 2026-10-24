# OPEN ROUTE #345 — AN ATTRIBUTE BASE OF A FOREIGN MODULE RESOLVES BY ITS TAIL TO A SAME-NAMED CLASS OF THE FILE
**Status: OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r345/`: `f01_import_tail_base.py`, `f02_import_tail_base_inv.py`.

`import rt25other as om; class S(om.B)` while this file also defines `class B` with `ensures \result == 1` (f01) or an invariant (f02): S inherits the LOCAL B's contract/invariant in the model; CPython `S().m()` is 2 (rt25other.B.m). Route #341 residual (3) assumed the tail resolution is only reached for a self-import; here the module is foreign. Helper `rt25other.py` in the witness dir.

Repair: Resolve an attribute base by its tail only for a provable self-import; any other module's class is an imported base.
