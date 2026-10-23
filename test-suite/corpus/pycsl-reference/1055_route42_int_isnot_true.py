"""Test 1055 — ROUTE #42 negative witness (c): `<int> is not True` was DECIDABLY FALSE.

FALSE OF THE PROGRAM: Python's `1 is not True` is True, so `f()` returns 7.

The NEGATED direction, and it is a distinct exploit rather than a restatement: here
the model proves the branch NOT taken, so a contract that is false of the program
proves through the FALL-THROUGH rather than through the branch. `ast.IsNot` mapped
onto `"!="`, so the guard read `not (!x = 1)`, decidably FALSE for `x = 1`. At the
parent commit 0f3906bd `\\result == 0` PROVED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = 1
    if x is not True:
        return 7
    return 0
