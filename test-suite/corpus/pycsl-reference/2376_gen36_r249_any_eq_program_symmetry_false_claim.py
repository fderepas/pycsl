r"""Test 2376 — route #249 (expected FAIL): Program side: under `if x == y` the test `y == x` was decided True, so `\result == 1` PROVED.
CPython `f(A(), B())` = 0.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if x == y:
        if y == x:
            return 1
        return 0
    return 1


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
