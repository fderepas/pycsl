# OPEN ROUTE #346 — A DATACLASS `__post_init__` IS NEVER EMITTED / VERIFIED — THE INVARIANT IS ASSUMED AFTER IT BREAKS IT
**Status: OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r346/`: `k08_dataclass_post_init.py`.

`@dataclass class D: x: int`, `#@ invariant x >= 0`, `__post_init__: self.x = -1` (a top-level store, admitted by R342). The generated `__init__` is checked (d01/m01/m05/m06 FAIL correctly) but `__post_init__` produces no goal: `f(d)` with `ensures d.x >= 0` PROVES; CPython -1.

Repair: Emit and verify `__post_init__` as part of construction (invariant goal after it), or refuse `__post_init__` on invariant-carrying classes.
