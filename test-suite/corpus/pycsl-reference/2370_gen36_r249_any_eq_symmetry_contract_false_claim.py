r"""Test 2370 — route #249 (expected FAIL): `requires x == y` PROVED `ensures y == x` on two `Any` parameters: `==` lowered to Why3 `=`, which is
symmetric. CPython: `A.__eq__ -> True`, `B.__eq__ -> False`; `A() == B()` is True, `B() == A()` False.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures y == x
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    class A:
        def __eq__(self, o: object) -> bool:
            return True

        def __hash__(self) -> int:
            return 0

    class B:
        def __eq__(self, o: object) -> bool:
            return False

        def __hash__(self) -> int:
            return 0

    x, y = A(), B()
    assert x == y and not (y == x)
