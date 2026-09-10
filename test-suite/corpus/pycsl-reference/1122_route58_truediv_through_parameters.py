"""Test 1122 — ROUTE #58 negative witness (b): the exact-real division decided the
ordering through PARAMETERS, so this was never constant-folding.

FALSE OF THE PROGRAM: with `a == 1` and `b == 3`, `a / b` is the double
`0.3333333333333333`, and `> 0.3333333333333333` is `False`.

THIS IS THE SHAPE THAT MADE THE ROUTE REACHABLE. A reader can dismiss 1121 as two
literals sitting next to each other and assume an over-eager fold. It is not: the
premises are enough for the prover to divide over the reals, so the everyday
contract `#@ ensures \result > 0.5` over a computed `a / b` was decided the same
way. The repair leaves any non-literal division UNINTERPRETED, so this fails closed
while 1124 shows the honest congruence claim still proves.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires a == 1
#@ requires b == 3
#@ ensures \result > 0.3333333333333333
#@ assigns \nothing
def f(a: int, b: int) -> float:
    return a / b
