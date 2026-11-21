r"""Test 2390 — route #249 (expected FAIL): Whole-list `==` on `List[Any]`: `requires xs == ys` PROVED `ensures ys == xs`. CPython `[A()]`, `[B()]`.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ requires xs == ys
#@ ensures ys == xs
#@ assigns \nothing
def f(xs: List[Any], ys: List[Any]) -> int:
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

    xs, ys = [A()], [B()]
    assert xs == ys and not (ys == xs)
