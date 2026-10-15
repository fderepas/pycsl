# OPEN ROUTE #238 — `<hval> or []` REPLACES ANY NON-MAP VALUE WITH THE EMPTY MAP

**Status: OPEN (gen #36, 2026-10-15), Severity 1.** Found by the ch12 chain agent; driver-reproduced at HEAD
0923aa92 (rc=0 "Verification SUCCESS").

## Witness (PROVED at HEAD; CPython `g({"args": [1, 2]})` = 2)
`witnesses-r238/or_list.py`: `a = d.get("args", []) or []`; `return len(a)` with `ensures \result == 0`.

## Mechanism
`expressions.py` `_recognize_pyval_or_default` (comment ~L5241) emits
`match v with HMap _ -> v | _ -> HMap PNil`: a truthy list / string / int is discarded.

## Repair direction
Faithful Python `or`: keep `v` when it is truthy (non-empty HArr/HMap/HStr, non-zero HInt, ...), else the
default; or opaque when truthiness of the shape is not modelled. Never a definite value for a truthy operand.
