# OPEN ROUTE #371 — HASHABILITY FOLLOWS ONLY THE FIRST BASE
**Status: OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r371/`: `h22_mixin_hash_none_second_base.py`, `h56_mixin_eq_second_base.py`, `h60_mixin_second_base_dc_eq.py`, `h63_mixin_third_base.py`, `h64_mixin_via_intermediate_second.py`, `h67_second_base_frozen_field.py`.

The inherited `__hash__` / `__eq__` lookup follows `bases[0]` only: `D(N, M)` with an unhashable mixin M is treated as hashable (control `D(M)` is refused). Slips past #364/#349. CPython TypeError unhashable.

Repair: Look up `__hash__` / `__eq__` along the full C3 MRO.
