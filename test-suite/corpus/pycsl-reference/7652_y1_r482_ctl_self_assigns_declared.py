r"""Test 7652 -- route #482 CONTROL (expected PASS at candidate; the advice followed): witness 7630's `\trusted` method declares its frame `#@ assigns self.xs`, so it is no longer refused; the caller's claim does not depend on `c.xs`.
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0]
        self.cnt = 0

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
    return c.cnt


if __name__ == "__main__":
    print("result", f(0), "expected 0")
