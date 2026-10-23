r"""Test 2388 — route #249 (expected FAIL): `requires x in s and x == y` PROVED `ensures y in s` on a `Set[Any]` (membership was key identity,
`==` was `=`). CPython: `s = {x}` for `x = A()` (`__eq__ -> True`, hash 0), `y = 1` (hash 1).
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any, Set


#@ requires x in s
#@ requires x == y
#@ ensures y in s
#@ assigns \nothing
def f(s: Set[Any], x: Any, y: Any) -> int:
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

    x, y = A(), 1
    s = {x}
    assert x in s and x == y and not (y in s)
