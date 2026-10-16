# OPEN ROUTE #254 — ONE dict/set PASSED TO A MUTATING SLOT AND A READ SLOT OF THE SAME CALL

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Found by the driver's red-team probe; driver-reproduced at
HEAD fa283db6 (both rc=0; CPython True).

## Witnesses (`witnesses-r254/`)
- `p21_set_param_double.py`: `g(x, y)` (`assigns x`) does `x.add(1)`, returns `1 in y` under
  `requires not (1 in y)`, `ensures \result == False`; caller `a = set(); return g(a, a)` proves `\result == False`.
- `p18_dict_param_double_req.py`: the dict version (`x[1] = 5`).

## Mechanism
The mutated parameter is a `ref`, the read-only one a value: `(g a !a)` — Why3's alias check compares refs only,
and the #243/#244 rule ("an argument in a mutating slot must be fresh or single-use") does not see `a` used twice
IN THE SAME CALL. The callee's contract is false whenever `x is y`. Lists are safe (Why3 "illegal alias").

## Repair direction
Extend the #243/#244 mutating-slot rule: an argument in a mutating slot must not also appear (or alias) in any
other argument of the same call; and/or treat the callee's read-only dict/set params as possibly aliasing its
mutated ones (havoc them after the mutation).
