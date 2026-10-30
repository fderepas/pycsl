r"""Test 7651 -- route #482 CONTROL (expected PASS: PROVED at base and candidate): a `\trusted` method with no `assigns` only READS `self` (a field into a test, `len`, a loop over a field), so it writes nothing and the caller keeps `c.xs[0]`.
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0]

    #@ \trusted
    def m(self) -> int:
        s = 0
        for y in self.xs:
            s = s + y
        if len(self.xs) > 0:
            return s
        return 0


#@ ensures \result == 0
def f(n: int) -> int:
    c = C()
    c.m()
    return c.xs[0]


if __name__ == "__main__":
    print("result", f(0), "expected 0")
