# OPEN ROUTE #310 — A TUPLE VALUE ASSIGNED TO A NAME IS HAVOCKED TO `(any ...)`, DROPPING THE EFFECTS OF CALLS INSIDE IT
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Found by the r307 executor (census); driver-reproduced on main (rc=0; CPython violates).
Witness `witnesses-r310/e_tuple_drop.py`: `xs = [0]; t = (inc(xs), 0); return xs[0]` with `ensures \result == 0` proves (CPython
returns 1); `inc` has `assigns a[0]`. The tuple assignment lowers to the havoc `(any int)` (unused-tuple / erased tuple local) so the
call `inc(xs)` and its write never happen in the model.
Repair direction: never havoc an expression that contains an effectful sub-expression (call with non-empty assigns/raises/unknown,
walrus, yield/await): either emit the effects (evaluate the elements in Python order, then havoc/erase only the VALUE) or refuse.
Census every erasure/havoc site that discards an expression (`any T` for erased values, unused tuple/record locals, discarded
expression statements, #252 erased reads) for effect-dropping.
