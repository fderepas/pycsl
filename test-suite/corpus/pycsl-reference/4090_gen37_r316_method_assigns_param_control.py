r"""Test 4090 -- gen #37 route #316 (expected PASS): CONTROL: a method declaring `#@ assigns xs[0]` and writing it is admitted (stub writes `x0`) and the caller proves about another list.
"""
# pycsl-expected: PASS
from typing import List
class P:
    def __init__(self) -> None:
        self.n = 0
    #@ requires len(xs) >= 1
    #@ assigns xs[0]
    def bump(self, xs: List[int]) -> None:
        xs[0] = 5

#@ ensures \result == 1
def f() -> int:
    ys = [0]
    zs = [1]
    p = P()
    p.bump(ys)
    return zs[0]

if __name__ == "__main__":
    assert f() == 1, f()
