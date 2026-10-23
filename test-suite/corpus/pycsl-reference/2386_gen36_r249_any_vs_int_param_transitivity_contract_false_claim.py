r"""Test 2386 — route #249 (expected FAIL): An `Any` against an `int` parameter: `requires x == n and y == n` PROVED `ensures x == y`. CPython:
`n = 5` and two instances of a class equal to the int 5 only.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == n and y == n
#@ ensures x == y
#@ assigns \nothing
def f(x: Any, y: Any, n: int) -> int:
    return 0


if __name__ == "__main__":
    class F:
        def __eq__(self, o: object) -> bool:
            return isinstance(o, int) and o == 5

    x, y = F(), F()
    assert x == 5 and y == 5 and not (x == y)
