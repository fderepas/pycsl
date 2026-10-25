# OPEN ROUTE #355 — `C(v)` ON AN ENUM HAS NO ValueError OBLIGATION
**Status: OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r355/`: `e16_intenum_ctor_valueerror.py`, `e31_enum_ctor_valueerror_plain.py`.

`x = C(99)` under no_exception is emitted `let x = (any c)` and proves for IntEnum (e16) and plain Enum (e31); CPython ValueError. (`C["Z"]` already gets a goal and fails.)

Repair: Under no_exception, `C(v)` asserts `v` is one of the member values (or refuse it), as `C[k]` already does.
