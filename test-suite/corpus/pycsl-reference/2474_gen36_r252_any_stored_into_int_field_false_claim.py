r"""Test 2474 — route #252 (expected FAIL): the store `b.v = x` puts an `Any` value into an `int` record
field; `b.v - b.v` then PROVED `\result == 0`. CPython: a user `__sub__` returns 7.
PROVED at 15f8c4bd; now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from typing import Any


class Box:
    def __init__(self, v: int):
        self.v: int = v


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    b = Box(0)
    b.v = x
    return b.v - b.v


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
