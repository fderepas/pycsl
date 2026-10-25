# OPEN ROUTE #383 — ELEMENT-CLASS SOURCES #372 DOES NOT DERIVE
**Status: OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r383/`: `h33_star_in_set.py`, `k14_type_alias.py`, `k15_dict_get.py`, `k17_dict_values_loop.py`, `k21_list_comp_subscript.py`, `k24_method_return.py`, `k25_any_param.py`, `k30_slice_elem.py`, `k38_items_loop.py`, `k39_alias_list_param.py`, `k40_alias_in_loop.py`, `k41_field_dict_get.py`, `k42_any_field.py`, `k43_method_return_self_field.py`, `k53_object_param.py`, `k54_typevar.py`.

Type aliases (`DD = D`, `DL = List[D]`), `m.get(..)`, loops over `.values()` / `.items()`, list comprehension then subscript, slice then subscript, method returns, `{*ds}`, and Any / object / TypeVar values or an Any field while the file has an unhashable class: `{..}` under no_exception proves; CPython TypeError.

Repair: Resolve module type aliases; element classes from `-> T` of methods and get/values/items, through comprehensions and slices; when underivable and the file has an unhashable class, refuse.
