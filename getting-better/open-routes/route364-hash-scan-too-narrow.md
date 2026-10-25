# OPEN ROUTE #364 — #349's CLASS-BODY HASHABILITY SCAN SEES ONLY `def __eq__` AND LITERAL `__hash__ = None`
**Status: OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r364/`: `h01_eq_lambda_assign_set.py`, `h02_hash_none_via_name.py`, `h21_hash_none_ifexp.py`, `h22_eq_under_if.py`, `h33_hash_none_tuple_assign.py`.

Missed: `__eq__ = lambda ...` (h01), `__hash__ = NOHASH` (h02), `__hash__ = None if ... else ...` (h21), `__eq__` under `if` (h22), `__hash__, tag = None, 1` (h33); a set element of such a record proves under no_exception; CPython TypeError unhashable.

Repair: Any class-body binding of `__eq__` (any statement / nesting) defines it; a `__hash__` binding to anything but a def is 'maybe None' => unhashable.
