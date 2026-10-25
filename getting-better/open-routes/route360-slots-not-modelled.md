# OPEN ROUTE #360 — `__slots__` IS NOT MODELLED — A STORE OUTSIDE THE SLOTS PROVES
**Status: OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r360/`: `a12_slots_store_unslotted.py`, `s02_slots_inherited_extra.py`, `s05_empty_slots_init_store.py`, `s06_slots_init_param.py`, `s08_slots_list_form.py`.

A constructor / method store of a name outside the union of `__slots__` over the MRO is lowered as an ordinary record field store (tuple, list, empty and inherited slots forms); CPython raises AttributeError at construction.

Repair: Compute the slots union over the MRO; when every in-file MRO class declares `__slots__`, refuse a `self.f` / `r.f` store whose name is outside it; refuse non-literal `__slots__`.
