r"""Test 2379 — route #249 (expected FAIL): Contract to body: `requires x == y` decided the program test `y == x`, so `\result == 1` PROVED.
CPython `f(A(), B())` = 0 (and `A() == B()` holds).
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if y == x:
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

    assert A() == B() and f(A(), B()) == 0
