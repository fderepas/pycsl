# OPEN ROUTE #250 — A `float` PARAMETER CAN BE NaN; THE `real` MODEL PROVES `x == x`, `x <= x`, TRICHOTOMY

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Residual of the #249 repair; driver-verified at the
repaired tree (= HEAD c5c703ad): all three rc=0. Route #45 closed the `float("nan")` LITERAL case only.

## Witnesses (`witnesses-r249/`)
- `float_nan_reflexivity.py`: `x: float`, `ensures x == x` PROVES (CPython: `nan == nan` is False).
- `float_nan_le_reflexivity.py`: `ensures x <= x` PROVES.
- `float_nan_ne_trichotomy.py`: `requires x != y`, `ensures x < y or y < x` PROVES.

## Mechanism
Python `float` is modelled as Why3 `real`, which has no NaN (nor ±inf): every real law (reflexivity,
totality of `<=`, trichotomy) holds for every float parameter, return value and field.

## Repair direction (needs a spike — the agent noted a "not NaN" guard makes every `\result == 1.5` unprovable
without an axiom)
Options: (a) model float as an IEEE type (Why3 `ieee_float` theory: Float64 with is_nan) — corpus-wide; (b) make
comparisons on float values that may be NaN uninterpreted unless a `requires not isnan(x)`/finite precondition or
a provenance from a literal/arithmetic on non-NaN values establishes non-NaN; (c) surface "floats are never NaN/inf"
as an explicit TCB assumption in the soundness report. Measure corpus blast radius (~13 root files compare
floats in contracts) before choosing.
