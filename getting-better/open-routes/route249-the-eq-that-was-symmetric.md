# OPEN ROUTE #249 — `==` ON `Any` IS MODELLED AS MATHEMATICAL EQUALITY; PYTHON `__eq__` NEED NOT BE

**Status: OPEN (gen #36, 2026-10-16), Severity 1 (design-level).** Residual of the #247/#248 repair;
driver-verified at the repaired tree (= HEAD 68ba005b): rc=0.

## Witness
`witnesses-r248/any_eq_symmetry.py`: `requires x == y`, `ensures y == x` PROVES. CPython: with
`A.__eq__ -> True` and `B.__eq__ -> False`, `A() == B()` is True and `B() == A()` is False.

## Mechanism
`==` on `Any`/erased values lowers to Why3 `=` (or an equivalence), so reflexivity/symmetry/transitivity
are free. Python only guarantees them for builtin types.

## Repair direction (design decision needed — record before building)
Options: (a) refuse `==`/`!=` between `Any` values in CONTRACTS (fail-closed; measure blast radius —
probably large); (b) lower `Any == Any` to an opaque binary predicate with no laws (program side fresh per
evaluation; contract side uninterpreted `py_eq x y`), keeping Why3 `=` only for declared builtin types;
(c) document "user __eq__ is an equivalence relation" as an explicit assumption in the soundness report
(the TCB) — only acceptable if surfaced, never silently.
