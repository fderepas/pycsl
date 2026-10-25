# OPEN ROUTE #356 — ENUM MEMBERS REACHED THROUGH CLASS-OBJECT ATTRIBUTES (`__members__`) KEEP INT LAWS
**Status: OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r356/`: `e20_members_values_loop.py`.

`for m in C.__members__.values(): m - m` under no_exception proves; CPython TypeError (plain Enum members).

Repair: Treat any load of a non-member attribute of an enum class (`__members__`, `_member_map_`, `_value2member_map_`, ...) as a member container and refuse it.
