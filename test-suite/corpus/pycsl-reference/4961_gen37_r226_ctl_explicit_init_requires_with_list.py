r"""Test 4961 -- gen #37 route #226: CONTROL: explicit `__init__(self, x: int, s: str, xs: List[int])` with `#@ requires x >= 0` under `#@ class invariant self.x >= 0` and a literal `self.n = 0` under `self.n >= 0`; the projection states `forall x n. x = x -> n = 0 -> x >= 0 -> (n >= 0) /\ (x >= 0)` and the file PROVES (CPython 1).
"""
from typing import List

#@ class invariant self.n >= 0
#@ class invariant self.x >= 0
class D:
    #@ requires x >= 0
    def __init__(self, x: int, s: str, xs: List[int]) -> None:
        self.x = x
        self.n = 0
        self.s = s
        self.xs = xs

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x + d.n

if __name__ == "__main__":
    assert f(D(1, "a", [])) == 1
