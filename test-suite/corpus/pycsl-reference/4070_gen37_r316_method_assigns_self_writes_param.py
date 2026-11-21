r"""Test 4070 -- gen #37 route #316 (expected FAIL): `#@ assigns self.n` method also does `xs[0] = 5`; the stub wrote only `self.n` and `ys[0] == 0` PROVED (CPython 5). REFUSED: PYCSL-METHOD-FRAME.
"""
# pycsl-expected: FAIL
from typing import List
class P:
    def __init__(self, n: int) -> None:
        self.n = n
    #@ requires len(xs) >= 1
    #@ assigns self.n
    def bump(self, xs: List[int]) -> None:
        self.n = 1
        xs[0] = 5

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    p = P(0)
    p.bump(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
