# OPEN ROUTE #303 — A DICT ALIASED THROUGH A TUPLE-UNPACKING ASSIGNMENT IS A VALUE COPY (bypasses #59 and r2c-local R1)
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Red-team round 11; driver-reproduced at 387d8da9 (4 probes rc=0; CPython violates).
Witnesses `witnesses-r303/`: `h, k = g, 1; h["G"] = 5; return g["G"]` proves `== 0` (CPython 5, l09); swap `g, h = h, h` (l12);
r2c-local path write-back through a tuple-bound alias of another local (l01) and of a PARAMETER root under `assigns \nothing`
(l08: the caller's dict is mutated). `h, k = g, 1` lowers to `let (_tu_h, _tu_k) = (!g, 1) in h := _tu_h` (a map copy). The
route #59 alias refusal (statements.py ~1459) and r2c-local's R1 ("every binding of the root is a dict literal") inspect plain
`x = y` assignments only. Repair: treat every TupleUnpack / swap / starred-free unpack whose value element is a mutable
collection name (or a call result per #283/#295) as an alias binding for #59/#279/#283/#295 AND for r2c R1; census every
binding form that can alias (tuple/list unpack, for-targets over containers of dicts, with-as, walrus inside tuples).
