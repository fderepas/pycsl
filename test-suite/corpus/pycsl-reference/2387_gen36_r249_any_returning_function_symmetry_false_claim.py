r"""Test 2387 — route #249 (expected FAIL): The result of a function returning `Any`: under `requires x == y`, `g(y) == g(x)` (with `g` the
identity, `ensures \result == x`) was decided, so `\result == 1` PROVED. CPython `f(A(), B())` = 0.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == x
#@ assigns \nothing
def g(x: Any) -> Any:
    return x


#@ requires x == y
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if g(y) == g(x):
        return 1
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

    assert f(A(), B()) == 0
