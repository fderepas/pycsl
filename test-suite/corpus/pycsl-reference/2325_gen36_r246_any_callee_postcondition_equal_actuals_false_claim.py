r"""Test 2325 — route #246 (expected FAIL): THROUGH A CALLEE CONTRACT. `g`'s postcondition
`\result == 1 <==> isinstance(x, int)` was about `typeof_op x`, so at two calls with `y1 == y2` the
results were forced equal and `\result == 1` PROVED at f777e2bd. CPython `m(1, 1.0)` = 0. This is
control 2212's mechanism with two `==` actuals: a contract-side `isinstance(<Any>, int)` is refused now.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0 or \result == 1
#@ ensures \result == 1 <==> isinstance(x, int)
#@ assigns \nothing
def g(x: Any) -> int:
    if isinstance(x, int):
        return 1
    return 0


#@ requires y1 == y2
#@ ensures \result == 1
#@ assigns \nothing
def m(y1: Any, y2: Any) -> int:
    a = g(y1)
    b = g(y2)
    if a == b:
        return 1
    return 0


if __name__ == "__main__":
    assert m(1, 1.0) == 0
