r"""Test 4954 -- gen #37 route #226 (expected FAIL): explicit `__init__(self, x: int, xs: List[int])` with `#@ requires len(xs) > 0` (a precondition about the LIST parameter only) under `#@ class invariant self.x >= 0`; no goal was stated and `ensures \result >= 0` on `d.x` PROVED (CPython `D(-1, [1]).x` is -1). The projection keeps only `#@ requires` conjuncts over the int parameters it binds, so the goal is `forall x. x = x -> x >= 0`, which FAILS.
"""
# pycsl-expected: FAIL
from typing import List

#@ class invariant self.x >= 0
class D:
    #@ requires len(xs) > 0
    def __init__(self, x: int, xs: List[int]) -> None:
        self.x = x
        self.xs = xs

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(-1, [1])) == -1
