r"""Test 7651 -- route #482 CONTROL (expected PASS: PROVED at base and candidate): a `\trusted` method with no `assigns` only READS `self` (a field bound to a local by `=`, then `len` and an element read into a test; no loop, so no assumed termination), so it writes nothing and the caller keeps `c.xs[0]`.
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0]

    #@ \trusted
    def m(self) -> int:
        ys = self.xs
        if len(ys) > 0 and ys[0] > 5:
            return ys[0]
        return 0


#@ ensures \result == 0
def f(n: int) -> int:
    c = C()
    c.m()
    return c.xs[0]


if __name__ == "__main__":
    print("result", f(0), "expected 0")
