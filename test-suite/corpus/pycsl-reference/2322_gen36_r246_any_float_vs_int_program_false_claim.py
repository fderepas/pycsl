r"""Test 2322 — route #246 (expected FAIL): the `float` analogue of 2321. `requires x == y` forced
`(typeof_op x) = 2` and `(typeof_op y) = 2` equal, so `\result == 1` PROVED at f777e2bd. CPython
`f(1.0, 1)` = 0 (`1.0 == 1`, only `1.0` is a float).
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    a = 0
    if isinstance(x, float):
        a = 1
    b = 0
    if isinstance(y, float):
        b = 1
    if a == b:
        return 1
    return 0


if __name__ == "__main__":
    assert f(1.0, 1) == 0
