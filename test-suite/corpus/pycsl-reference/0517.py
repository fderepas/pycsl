"""Test 0517 — float is Why3 `real`, not int (no-more-int Stage D), and the arithmetic
bridge is UNINTERPRETED (route #53).

`float` params/locals/returns are Why3 `real`; float literals (`0.0`) are real constants,
replacing the **unsound** `τ(float)=int` that truncated literals and used int arithmetic.
Float arithmetic (`x + x`) lowers through a `float_add_op` bridge, and since route #53 that
bridge is one UNINTERPRETED DETERMINISTIC symbol — `val function float_add_op (a b: real)
: real` — used by the SPEC path and the BODY path alike.

WHAT THIS FILE STILL PROVES, AND WHY. The additive relationship `\result == x + x` holds by
CONGRUENCE: the body's term and the contract's term are the same term. Determinism is what
buys that, and it is the whole reason the repair did not simply drop the bridge's contract.

WHAT THIS FILE DELIBERATELY NO LONGER CLAIMS — READ THIS BEFORE ADDING IT BACK. The clause
`ensures \result >= 0.0`, under `requires x >= 0.0`, used to prove and does not any more.
It is TRUE of the program, so its loss is COMPLETENESS, not soundness; it is the single
measured cost of route #53 across the whole corpus (2 of 916 emissions moved, and 0518 —
the negative twin — still fails as it must).

It is NOT repairable by giving the bridge an IEEE-true-looking sign clause. `a >= 0.0 ->
b >= 0.0 -> result >= 0.0` reads as sound, but the antecedent ranges over the Why3 `real`,
which does not distinguish NaN from an ordinary value, and the identical shape was already
measured to REFUTE for `*`: the clauses meet at `a = 0.0` and decide `result = 0.0`, while
Python's `0.0 * float("inf")` is `nan`. Recovering sign and bound facts honestly needs the
error-carrying or `ieee_float.Float64` lowering recorded as route #53's real repair — not a
clause bolted onto an uninterpreted symbol."""
_ = 0  # anchor


#@ requires x >= 0.0
#@ ensures \result == x + x
#@ assigns \nothing
def double(x: float) -> float:
    return x + x
