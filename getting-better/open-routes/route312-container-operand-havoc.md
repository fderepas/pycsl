# OPEN ROUTE #312 — A SLICE / sorted(...) / list_new OPERAND COERCED TO `(any int)` DROPS THE CALLS INSIDE IT (#310 marks displays only)
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witnesses `witnesses-r312/`: `ys[0:inc(xs)][0]` -> `subscript_get (any int) 0` (d01); sum/max/count/index of a slice (d04, h07);
`for _ in ys[0:inc(xs)]` (d05); `sorted([inc(xs), 0])[0]` (e03); `print(slice)` (i08); unannotated param `g(ys[0:inc(xs)])` (r01);
constructor arg (v02). Mechanism: `_coerce_to_int` (expressions.py ~1175) erases any text starting with `Array.sub`, `array_slice`,
`sorted_1`, `list_new_arr`; #310's effect marking covers tuple/set/list/dict DISPLAYS only.
Repair: apply #310's rule to EVERY erased/coerced expression (evaluate the effectful sub-expressions in Python order then erase the
value, or refuse) — key the check on the IR expression's effectfulness, not on the emitted text prefix.
