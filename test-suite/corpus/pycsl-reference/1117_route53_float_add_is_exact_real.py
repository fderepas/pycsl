"""Test 1117 — ROUTE #53 negative witness (a): a Python `float` was modelled as the
EXACT real, so `0.1 + 0.2 == 0.3` PROVED.

FALSE OF THE PROGRAM: Python's `0.1 + 0.2` is `0.30000000000000004`, and
`0.1 + 0.2 == 0.3` is `False`. The contract below claims it is `0.3`.

WHY IT PROVED, AND WHY THAT IS THE DOCUMENTED MODEL. `τ(float) = real`, and Why3's
`real` is the exact mathematical real, in which `1/10 + 2/10` really is `3/10`.
Python's `float` is IEEE 754 binary64, in which it is not: neither tenth is
representable, and the rounded sum lands one ulp above three tenths. The static-
semantics reference introduced `τ(float) = real` as the FIX for the unsound
`τ(float) = int` that truncated literals — a real improvement — but nothing said
the replacement is EXACT where the language ROUNDS. A limitation nobody wrote down
is one every reader assumes away.

WHERE THE EXACTNESS ENTERED. Not in the type. The float arithmetic bridge carried
its own defining contract, `val float_add_op (a b: real) : real
ensures { result = (a +. b) }`, and the SPEC path did not even go through the
bridge — it emitted `(a +. b)` outright. So both sides of the postcondition were
Why3's exact real addition and the goal closed by arithmetic.

THE FIX makes the bridge ONE UNINTERPRETED, DETERMINISTIC symbol
(`val function float_add_op (a b: real) : real`) used by the spec path and the body
path alike. Uninterpreted is what stops any exact-real fact from being decided;
DETERMINISTIC is what keeps the honest congruence claim provable — 1120 is that
positive control.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0.3
#@ assigns \nothing
def f() -> float:
    return 0.1 + 0.2
