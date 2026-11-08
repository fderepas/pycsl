r"""Test 2381 — route #249 (expected FAIL): Elements of a `List[Any]` are `int` cells: `requires xs[0] == xs[1]` PROVED `ensures xs[1] == xs[0]`.
CPython `[A(), B()]`.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ requires len(xs) == 2
#@ requires xs[0] == xs[1]
#@ ensures xs[1] == xs[0]
#@ assigns \nothing
def f(xs: List[Any]) -> int:
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

    xs = [A(), B()]
    assert xs[0] == xs[1] and not (xs[1] == xs[0])
