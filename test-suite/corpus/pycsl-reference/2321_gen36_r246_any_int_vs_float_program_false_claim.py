r"""Test 2321 — route #246 (expected FAIL): in a PROGRAM body, `isinstance(x, int)` and
`isinstance(y, int)` were `(typeof_op x) = 0` and `(typeof_op y) = 0`, so `requires x == y` forced
them equal and `\result == 1` PROVED at f777e2bd. CPython `f(1, 1.0)` = 0. Each parameter's tag is
now keyed on the PARAMETER (its identity), never on its stored value, so the two tests are independent.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if isinstance(x, int):
        if not isinstance(y, int):
            return 0
    return 1


if __name__ == "__main__":
    assert f(1, 1.0) == 0
