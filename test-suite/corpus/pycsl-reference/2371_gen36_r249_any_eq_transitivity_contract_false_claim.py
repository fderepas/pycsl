r"""Test 2371 — route #249 (expected FAIL): `requires x == y and y == z` PROVED `ensures x == z` on `Any` parameters (Why3 `=` is transitive).
CPython: `x = 1`, `y = A()`, `z = 2` (`A.__eq__ -> True`): `1 == A()` (reflected to `A.__eq__`) and
`A() == 2` are True, `1 == 2` is False.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y and y == z
#@ ensures x == z
#@ assigns \nothing
def f(x: Any, y: Any, z: Any) -> int:
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

    x, y, z = 1, A(), 2
    assert x == y and y == z and not (x == z)
