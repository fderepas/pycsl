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

## Measurement and spike (gen #36, 2026-10-16) — status stays OPEN, nothing built

### Census (base aaf9b355)
19 root corpus files have a `float` parameter/return, all with a comparison in a contract; 2 pyref files
mention `float`. There is NO spec-level `math.isnan`/`math.isfinite` (not modelled, no stub); the only
non-NaN test a user can write is Python's own `x == x`. Float ARITHMETIC is already law-free (route #53:
`float_add_op` etc. are uninterpreted); only comparisons and `=` are decided over `real`.

### Spike (hand `.mlw`, axiom-free; `scratchpad/r251/spike/`, `spike-guard.log`)
- (a) **NaN as the non-dyadic real `1/3`**: `constant pycsl_float_nan : real = 1.0 /. 3.0` (a DEFINITION).
  Every finite binary64 value is dyadic and every PyCSL float literal is a finite decimal, so neither can be
  `1/3`; a float parameter or an uninterpreted op result MAY be. A comparison lowers to the real comparison
  conjoined with `<> pycsl_float_nan` on each operand (`!=` its negation; `x == x` becomes exactly "x is not
  NaN"). `a_nan_third.mlw`: the three route witnesses are Unknown on Z3 and Alt-Ergo; `\result == 1.5`,
  decimal literals, `from_int n`, `<`-asymmetry, transitivity, `x > 0 -> x >= 0`, `==`-symmetry all prove
  (< 1 s). This is the sound narrow rule the route asked for.
- **Its blast radius is NOT acceptable under M1**, measured by hand-guarding the emitted `.mlw` of the
  corpus' float-equality files (`spike/c/g/`): 0845 (literal-pinned) still PROVES; 0818 (`\result ==
  a[i]`), 0847 (`\result == v`), 1120 (`\result == x + x`) go FAIL — justified, each is FALSE in CPython for
  a NaN input; but **0517** (`requires x >= 0.0 ensures \result == x + x`) and **1124** (`\result == a / b`
  for ints) go FAIL although TRUE in CPython: the uninterpreted `float_add_op`/`float_truediv_op` result may be
  the sentinel, and nothing short of an IEEE law ("non-NaN + non-NaN is not NaN" is itself false for
  `inf - inf`) restores them. Every `ensures \result == <float arithmetic>` dies the same way.
- (b) **Why3 `ieee_float.Float64`** (`b_float64.mlw`): the witnesses are refuted-unknown, the controls prove
  on Z3, but (i) literals must be EXACTLY representable — `(0.1:t)` is a parse error ("Invalid floating point
  literal"), so every decimal literal must be rounded to a hex literal at emission; (ii) Alt-Ergo times out
  (32 s for the file) on the three refuted goals; (iii) it changes the float sort corpus-wide (every float
  file moves, route #53's `real` bridges, `from_int`, the literal fold of route #58).
- (c) **Surface the assumption**: not built here; the soundness report has no float/NaN entry today.

### Verdict
No narrow rule with an M1-acceptable blast radius: (a) is sound but costs two TRUE corpus claims (0517, 1124)
plus every equality on a float arithmetic result; (b) is a corpus-wide sort change. Recommended next step:
(a) together with a spec-level `math.isnan`/`math.isfinite` and a finite-provenance fact for route #53's
ops (needs an IEEE-faithful op model), or (c) as an interim, declared TCB entry. Not measured here (candidate
residuals for whoever builds (a)): comparisons that do not go through `_handle_binop` (e.g. a `max`/`min`
lowering; Python's `max(nan, 1.0)` is `nan`) would bypass the guard, and signed zero (`0.0 == -0.0`, then
`math.copysign`) is a separate `real`-model gap.
