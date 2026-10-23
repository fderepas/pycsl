r"""Test 4077 -- gen #37 route #316 (expected FAIL): method writes `xs[1]`; a caller frame `ys[1] == \old(ys[1])` PROVED (CPython 1). FAILS.
"""
# pycsl-expected: FAIL
from typing import List
class P:
    def __init__(self) -> None:
        self.n = 0
    #@ requires len(xs) >= 2
    def poke(self, xs: List[int]) -> int:
        xs[1] = xs[0] + 1
        return xs[1]

#@ requires len(ys) >= 2
#@ ensures ys[1] == \old(ys[1])
def f(ys: List[int]) -> None:
    p = P()
    p.poke(ys)

if __name__ == "__main__":
    a = [0, 0]
    f(a)
    assert a[1] == 0, a
