r"""Test 2377 — route #249 (expected FAIL): Program side: `if x == x` was decided True on an `Any` parameter, so `\result == 1` PROVED.
CPython `f(float("nan"))` = 0.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    if x == x:
        return 1
    return 0


if __name__ == "__main__":
    assert f(float("nan")) == 0
