# OPEN ROUTE #354 — IntFlag IS TREATED AS int — `~`, STRICT-BOUNDARY `|` / `^` ARE MISLOWERED
**Status: OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r354/`: `e05_intflag_invert.py`, `e39_intflag_strict_or.py`, `e40_intflag_strict_ctor_int.py`.

`~x` on an IntFlag member is lowered `(-x)-1` (e05: `x + ~x == -1` proved; CPython 3, `~A == B`); `class F(IntFlag, boundary=STRICT)`: `x | 4` / `x ^ 8` under no_exception prove (CPython ValueError).

Repair: Take IntFlag (and Flag) out of the int-like set, or refuse `~ | & ^` on their members; any class keyword (`boundary=`) makes the enum opaque.
