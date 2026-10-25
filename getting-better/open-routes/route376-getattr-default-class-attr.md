# OPEN ROUTE #376 — `getattr(o, "k", d)` FOLDS TO THE DEFAULT FOR A CLASS ATTRIBUTE OR METHOD
**Status: OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r376/`: `e47_getattr_class_attr_record.py`, `e48_getattr_inherited_attr.py`, `e96_getattr_self_class_attr_record.py`, `e98_getattr_method_record_value.py`.

Folded to the default whenever `k` is not an instance field: a class attribute (own or inherited, e47/e96/e48) or a method (e98) exists, so CPython returns it (-1 / a bound method), not the default.

Repair: Fold to the default only when no class-body binding of that name exists anywhere in the MRO (and no `__getattr__`); otherwise refuse.
