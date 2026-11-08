r"""Test 7653 -- route #482 (expected FAIL: NOT PROVED at candidate; the advice followed keeps the claim honest): witness 7630's method with `#@ assigns self.xs` declared -- the caller can no longer prove `c.xs[0]` unchanged (CPython returns 7).
"""
# pycsl-expected: FAIL
from typing import List


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0]

    #@ \trusted
    #@ assigns self.xs
    def m(self) -> int:
        ys = (self.xs,)[0]
        ys[0] = 7
        return 0


#@ ensures \result == 0
def f(n: int) -> int:
    c = C()
    c.m()
    return c.xs[0]


if __name__ == "__main__":
    print("result", f(0), "expected 0")
