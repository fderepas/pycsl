"""Test 1241 — ROUTE #90, SECOND OPERATOR: `is not True` lies the same way.

NOT TRUE OF THE PROGRAM. `1 is not True` is True in CPython, so f(1) returns 1, not 0.
MEASURED: f(1) = 1. The operator arm matters because a repair that fixed only `is True`
would leave this one proving.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires x == 1
#@ ensures \result == 0
#@ assigns \nothing
def f(x: bool) -> int:
    if x is not True:
        return 1
    return 0
