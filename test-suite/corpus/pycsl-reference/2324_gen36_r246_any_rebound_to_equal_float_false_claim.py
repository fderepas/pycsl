r"""Test 2324 — route #246 (expected FAIL): a REBINDING to an `==` value of another type. Both tests
read `(typeof_op !x) = 0` and `x := y` with `x == y` left `!x` unchanged, so `\result == 1` PROVED at
f777e2bd. CPython `f(1, 1.0)` = 0. A test on a rebound name is now a fresh value per evaluation.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    a = 0
    if isinstance(x, int):
        a = 1
    x = y
    b = 0
    if isinstance(x, int):
        b = 1
    if a == b:
        return 1
    return 0


if __name__ == "__main__":
    assert f(1, 1.0) == 0
