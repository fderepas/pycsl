r"""Test 7631 -- route #482 (expected FAIL: PROVED at base, REFUSED PYCSL-R482-TRUSTED-FRAME-UNTRACKED): a `\trusted` method with no `assigns` stores `self.xs[0] = 7` DIRECTLY (its call stub takes `writes` from `assigns` only); CPython returns 7.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0]

    #@ \trusted
    def m(self) -> int:
        self.xs[0] = 7
        return 0


#@ ensures \result == 0
def f(n: int) -> int:
    c = C()
    c.m()
    return c.xs[0]


if __name__ == "__main__":
    r = f(0)
    print("result", r, "expected 0")
