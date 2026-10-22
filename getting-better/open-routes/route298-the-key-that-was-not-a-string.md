# OPEN ROUTE #298 — THE hval MODEL ASSUMES EVERY NESTED DICT HAS str KEYS (undeclared)
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Found by the r296 executor; driver-reproduced at 249ded4d (rc=0; CPython False).
Witness `witnesses-r298/c08_items_local.py`: `xs = d["xs"]; for k, v in xs.items(): return isinstance(k, str)` with
`ensures \result == True` proves; CPython `f({"xs": {1: 2}})` is False. `Dict[str, PyVal]` constrains only the TOP-level keys; a
nested `PyVal` dict may have int/tuple/None keys, but the hval carrier `HMap (pairs of string * hval)` (and every key view:
`.items()/.keys()`, bare iteration after #296, `in`, `.get` with a non-str key) models them as strings. Repair: either a faithful
key carrier (hval key = hval) or refuse/opaque every key-typed observation of a nested hval map whose key type is not
proven str, or DECLARE the assumption (HVAL-STR-KEYS, `--soundness-report` relied_on_by every nested-key read, +docs, strict
mode refusing) per the FLOAT-FINITE/LATIN1-STR precedent — measure the corpus/mirror cost of each and choose.
