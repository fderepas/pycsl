# OPEN ROUTE #299 — A STARRED ELEMENT IN A LIST LITERAL STORED AS AN hval BECOMES ONE ELEMENT
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Red-team round 10; driver-reproduced at 2cef1801 (4 probes rc=0; CPython violates).
Witnesses `witnesses-r299/`: `{"a": [*range(2), 3]}` gives `len(d.get("a")) == 2` (CPython 3, b10); `bool([*range(0)])` true (m01);
`"q" in [*"q"]` false (m02); `[*(...), {...}]` through the ch30 `hval_to_seq` bridge counts 2 (CPython 3, g01). `_pyval_wrap`
(src/pycsl/module6_whyml/expressions.py ~1320) wraps each ArrayLit element as one HCons, so a Starred element becomes a single
`HInt <...>`. #297 fixed only the types.py fold. Repair: a list/tuple/set/dict literal with any Starred (or **) element must not be
wrapped element-wise (opaque/uninterpreted hval or refuse); census every literal->hval wrapping path.
