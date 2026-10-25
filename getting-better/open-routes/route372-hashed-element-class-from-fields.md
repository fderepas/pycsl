# OPEN ROUTE #372 — THE CLASS OF A HASHED ELEMENT IS NOT DERIVED FROM FIELDS OR SUBSCRIPTS
**Status: OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r372/`: `h18_list_index_not_hash.py`, `h52_record_field_elem_set.py`, `h55_tuple_index_elem_set.py`, `h70_self_field_elem_set.py`, `h73_dict_items_value.py`.

`{r.d}`, `{self.d}` (typed record fields), `{t[0]}`, `{m[0]}`, `{xs[0]}` (subscripts of fully annotated tuple / dict / list parameters) are never hash-checked; h18 is #349 residual (1). CPython TypeError unhashable.

Repair: Derive the element class from field annotations and Tuple / Dict / List subscripts; refuse when unknown.
