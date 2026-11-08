r"""Test 2392 — route #249 (expected FAIL): A record field declared `Any`: `requires a.w == b.w` PROVED `ensures b.w == a.w`. CPython
`R(1, A())`, `R(1, B())`.
PROVED at fded262c.
"""
# pycsl-expected: FAIL
from typing import Any


class R:
    def __init__(self, v: int, w: Any) -> None:
        self.v = v
        self.w = w


#@ requires a.w == b.w
#@ ensures b.w == a.w
#@ assigns \nothing
def f(a: R, b: R) -> int:
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

    a, b = R(1, A()), R(1, B())
    assert a.w == b.w and not (b.w == a.w)
