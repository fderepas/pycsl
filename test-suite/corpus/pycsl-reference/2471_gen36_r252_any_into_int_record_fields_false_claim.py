r"""Test 2471 — route #252 (expected FAIL): `Box(x, x)` stores an `Any` value into two `int` record
fields, after which `b.v - b.w` was Why3 integer subtraction and PROVED `\result == 0`.
CPython: a user `__sub__` returns 7. PROVED at 15f8c4bd; the flow is now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from typing import Any


class Box:
    def __init__(self, v: int, w: int):
        self.v: int = v
        self.w: int = w


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    b = Box(x, x)
    return b.v - b.w


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
