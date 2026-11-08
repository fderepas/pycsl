r"""Test 2373 — route #249 (expected FAIL): `requires x != y` PROVED `ensures not (x == y)`: `!=` lowered to `<>`, the negation of `=`. Python
calls `__ne__`, its own method. CPython: a class whose `__eq__` and `__ne__` both return True.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x != y
#@ ensures not (x == y)
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    class N:
        def __eq__(self, o: object) -> bool:
            return True

        def __ne__(self, o: object) -> bool:
            return True

    x, y = N(), N()
    assert x != y and x == y
