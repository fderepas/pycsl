"""Test 1045 — ROUTE #41 negative witness (e): ARITHMETIC on an erased local.

FALSE OF THE PROGRAM: `(1,2) + 5` raises `TypeError` in Python.
At the parent commit c37f0059 `\result == 5` PROVED, from `x := 0; !x + 5`. See 1041.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x = (1, 2)
    return x + 5
