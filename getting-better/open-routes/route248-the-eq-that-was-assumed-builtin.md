# OPEN ROUTE #248 — THE MODEL ASSUMES BUILTIN `==` FOR `Any` VALUES; A USER `__eq__` BREAKS IT

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Residual recorded by the #245 and #246 repairs;
driver-verified to PROVE at the #246 candidate tree (= HEAD 1a86a361).

## Witness
`witnesses-r246/user_eq_str.py`: `f(x: Any, y: Any)` with `requires x == y` and
`ensures isinstance(x, str) == isinstance(y, str)` PROVES. CPython: `W() == "s"` is True for
`class W: def __eq__(self, o): return True`, and the postcondition is False.

## Mechanism
`==` on `Any`/erased values is modelled as structural/value equality of the lowered value, and the
str/list/dict isinstance answers (kept value-applied by #245/#246, control 2331) rely on `==` never
crossing types — true for builtins only.

## Repair direction
Either refuse contract reasoning that combines `==` on `Any` with type tests (fail-closed), or require the
subject to be builtin-typed (a declared non-Any type), or model user classes' `__eq__` (out of scope).
Measure the corpus blast radius first: control 2331 encodes exactly this assumption.
