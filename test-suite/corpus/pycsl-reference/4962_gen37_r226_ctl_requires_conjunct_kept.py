r"""Test 4962 -- gen #37 route #226: CONTROL: `#@ requires x >= 0 and len(xs) == x` on `__init__(self, x: int, xs: List[int])` under `#@ class invariant self.x >= 0`; the projection keeps the conjunct over the int parameter (`x >= 0`) and drops the one over the list (dropping a premise only strengthens the goal), so the goal discharges and the file PROVES (CPython 0).
"""
from typing import List

#@ class invariant self.x >= 0
class D:
    #@ requires x >= 0 and len(xs) == x
    def __init__(self, x: int, xs: List[int]) -> None:
        self.x = x
        self.xs = xs

#@ ensures \result >= 0
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    assert f(D(0, [])) == 0
