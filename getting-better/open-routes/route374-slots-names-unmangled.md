# OPEN ROUTE #374 — `__slots__` NAMES ARE COMPARED UNMANGLED
**Status: OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r374/`: `s05_slots_mangled_subclass.py`, `s21_slots_mangled_external.py`, `s22_slots_mangled_own_class_ok_read.py`, `s27_slots_mangled_external_read.py`, `s29_slots_dc_slots_mangled.py`.

Slot names and store names are compared as written: `self.__x` in a subclass (`_B__x`) and `a.__x` outside the class pass #360 (CPython AttributeError: no `__dict__`); conversely s28 over-refuses the real slot `self._A__x`.

Repair: Mangle both sides (per defining class) before comparing.
