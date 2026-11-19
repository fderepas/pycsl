r"""Test 4072 -- gen #37 route #316 (expected FAIL): method with no `assigns` does `xs[0] = 5`; `ys[0] == 0` PROVED (CPython 5). The stub now writes `x0`: FAILS.
"""
# pycsl-expected: FAIL
from typing import List
class P:
    def __init__(self, n: int) -> None:
        self.n = n
    #@ requires len(xs) >= 1
    def bump(self, xs: List[int]) -> None:
        xs[0] = 5

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    p = P(0)
    p.bump(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
