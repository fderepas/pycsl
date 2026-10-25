# OPEN ROUTE #378 — A DATACLASS FIELD DEFAULT IS READ FROM THE FIRST CLASS-BODY BINDING
**Status: OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r378/`: `a47_dc_field_then_rebind.py`, `a48_dc_reannotated.py`.

`n: int = field(default=3, init=False)` then `n = -1` (a47), or the field re-annotated (a48): goal `n = 3`; dataclasses reads the class `__dict__` after the body ran, so CPython `d.n` is -1.

Repair: Use the last binding, or refuse a dataclass field name rebound in the class body.
