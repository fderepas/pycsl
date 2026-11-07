"""Test 1242 — ROUTE #90, THIRD OPERATOR: `is False` lies the same way.

NOT TRUE OF THE PROGRAM. `requires x == 0` is satisfied by the int `0`, and `0 is False`
is **False** in CPython, so f(0) returns 0, not 1. MEASURED: f(0) = 0.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires x == 0
#@ ensures \result == 1
#@ assigns \nothing
def f(x: bool) -> int:
    if x is False:
        return 1
    return 0
