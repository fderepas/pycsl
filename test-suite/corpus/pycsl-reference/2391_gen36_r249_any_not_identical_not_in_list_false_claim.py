r"""Test 2391 — route #249 (expected FAIL): `x is not y` then `x in [y]`: membership was read as `x = y`, so it was decided False and
`\result == 0` PROVED. CPython `f(B(), A())` = 1 (`[A()]` contains anything).
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if x is not y:
        if x in [y]:
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

    assert f(B(), A()) == 1
