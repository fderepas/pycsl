r"""Test 2383 — route #249 (expected FAIL): `x in [y]` lowered to `x = y`, so the following `y == x` was decided and `\result == 1` PROVED.
Python's list membership is `y is x or y == x`: CPython `f(nan, nan)` (one object) = 0.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if x in [y]:
        if y == x:
            return 1
        return 0
    return 1


if __name__ == "__main__":
    n = float("nan")
    assert f(n, n) == 0
