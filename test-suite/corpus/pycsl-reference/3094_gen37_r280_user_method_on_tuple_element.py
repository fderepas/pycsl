r"""Test 3094 — route #280 (expected FAIL): a USER method that writes its receiver (`bump`, `assigns
self.v`) called on a tuple element `t[0].bump()` became an int op with no `writes`; `c.v == 0`
PROVED at 72ab1c57 (census probe q1). CPython: 1. Now refused.
"""
# pycsl-expected: FAIL
from typing import Tuple


class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    def bump(self) -> None:
        self.v = self.v + 1


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    t: Tuple[C, int] = (c, 1)
    t[0].bump()
    return c.v


if __name__ == "__main__":
    assert f() == 1
