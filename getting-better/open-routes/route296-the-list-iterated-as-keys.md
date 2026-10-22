# OPEN ROUTE #296 — AN hval LOCAL HOLDING A LIST, ITERATED AS A BARE VARIABLE, IS ITERATED AS DICT KEYS
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Found by the ch30 drain; driver-reproduced at 873ead89 (rc=0; CPython False).
Witness `witnesses-r296/fp_list_as_keys.py`: `xs = d.get("xs") or []; for x in xs: return isinstance(x, str)` with
`ensures \result == True` proves; CPython `first_is_str({"xs": [{"k": 1}]})` is False. The bare `for x in <pyval local>`
branch of `_classify_iterable` (stmt_control_flow.py; the dict-KEY arm, Tier-5 union/match cluster) treats every pyval local as a
dict and binds x to an arbitrary key string. Repair: take the key path only when the local is provably a dict (HMap / dict
literal / dict-typed source); a list carrier must take the R2b element path (or decline). The same branch serves the converted
`_maybe_inject_union_return` -> corpus + mirror byte-diff and re-proof of movers required.
