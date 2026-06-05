"""Test 0517 — float is Why3 `real`, not int (no-more-int Stage D).

`float` params/locals/returns are now Why3 `real`; float literals (`0.0`) are real constants;
float arithmetic (`x + x`) lowers through a `float_add_op` real bridge (RealInfix `+.`), replacing
the **unsound** `τ(float)=int` that truncated literals and used int arithmetic. Here `double`
proves the additive relationship and a non-negativity bound over the reals."""
_ = 0  # anchor


#@ requires x >= 0.0
#@ ensures \result == x + x
#@ ensures \result >= 0.0
#@ assigns \nothing
def double(x: float) -> float:
    return x + x
