r"""Test 2389 — route #249 (expected FAIL): Whole-tuple `==` on `Tuple[Any, int]`: `requires t == u` PROVED `ensures u == t` (Python compares
the `Any` slots with their own `__eq__`). CPython `(A(), 1)`, `(B(), 1)`.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any, Tuple


#@ requires t == u
#@ ensures u == t
#@ assigns \nothing
def f(t: Tuple[Any, int], u: Tuple[Any, int]) -> int:
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

    t, u = (A(), 1), (B(), 1)
    assert t == u and not (u == t)
