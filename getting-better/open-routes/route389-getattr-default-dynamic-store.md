# OPEN ROUTE #389 — `getattr` DEFAULTS DESPITE A `setattr` / MANGLED STORE CREATING THE ATTRIBUTE
**Status: OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r389/`: `g09_getattr_instance_setattr_method.py`, `g12_getattr_mangled_name.py`, `g21_setattr_computed_name_then_getattr.py`, `g22_getattr_dc_initfalse_absent_field.py`.

`setattr(self, "k" or a computed name, ..)` in `__init__` / `__post_init__`, and `getattr(r, "_R__k", 0)` against the mangled store `self.__k`: the default is used; CPython 5.

Repair: Allow the default only when no setattr / object.__setattr__ / __dict__ store with a non-constant or non-field name targets the class; compare getattr names against mangled field spellings.
