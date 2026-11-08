"""Test 1118 — ROUTE #53 negative witness (b): the same exact-real decision reached
through a PARAMETER, not just through literals.

FALSE OF THE PROGRAM: with `x` bound to `0.1`, Python's `x + 0.2` is
`0.30000000000000004`, so `\result == 0.3` is `False`.

This file exists because the literal-only shape (1117) invites the reading "constant
folding over-eager on two literals". It is not folding. The `requires x == 0.1`
premise plus exact-real addition is enough for the prover to decide the sum, so the
route reaches any float the contract can pin — a parameter, a field, a returned
value — and not only a pair of constants sitting next to each other in the source.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires x == 0.1
#@ ensures \result == 0.3
#@ assigns \nothing
def f(x: float) -> float:
    return x + 0.2
