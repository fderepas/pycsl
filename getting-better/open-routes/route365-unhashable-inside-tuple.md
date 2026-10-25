# OPEN ROUTE #365 — AN UNHASHABLE RECORD INSIDE A TUPLE IN A HASHING POSITION IS NOT CHECKED
**Status: OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r365/`: `h15_unhashable_in_tuple_set.py`, `h16_tuple_hash.py`, `h26_tuple_elem_set_typed.py`, `h29_dict_tuple_key.py`.

`{(d, 1)}`, `hash((d, 2))`, `{t}` with `t: Tuple[D, int]`, `{(d, 1): 0}`: only the element expression itself is checked; CPython TypeError unhashable.

Repair: In every hashing position recurse into tuple displays and `Tuple[...]` annotation arguments.
