# OPEN ROUTE #366 — HASHABILITY OF IMMUTABLE-RECORD FIELDS IS COMPUTED IN ONE ORDERED PASS AND MISSES object/Any/unsafe_hash
**Status: OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r366/`: `h08_frozen_object_field.py`, `h23_unsafe_hash_list_field.py`, `h24_frozen_field_forward_ref_order.py`, `h25_frozen_field_forward_ref_dc.py`, `h27_frozen_tuple_field_of_dc.py`, `h31_namedtuple_object_field.py`.

A field class declared later (`z: "Z"`, h24/h25) is missed by the single name-ordered pass; `object` / `Any` fields accept any value (h08, h31); `unsafe_hash=True` records are never field-checked (h23); `Tuple[Z, int]` contributes only its head (h27). CPython TypeError (unhashable list / record field).

Repair: Fixpoint over all classes; `object` / `Any` / unknown field annotations and every Tuple/Union argument possibly unhashable; field check applies to unsafe_hash records.
