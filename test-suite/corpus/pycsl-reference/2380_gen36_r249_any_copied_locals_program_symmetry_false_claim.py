r"""Test 2380 — route #249 (expected FAIL): Locals bound from `Any` parameters: `a = x; b = y; if a == b: if b == a` was decided, so `\result ==
1` PROVED. The erased-name pre-scan follows the binding. CPython `f(A(), B())` = 0.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    a = x
    b = y
    if a == b:
        if b == a:
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
