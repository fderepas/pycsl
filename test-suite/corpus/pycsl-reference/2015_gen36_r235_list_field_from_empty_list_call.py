r"""Test 2015 — route #235 (expected PASS): CONTROL for 2013. `self.items = list()` takes no
parameter and IS empty, so the faithful `(Array.make 0 0)` is kept and `\result == 0` still
PROVES. Bounds the repair: only a store over a parameter (or a non-literal) is unconstrained.
"""
# pycsl-expected: PASS
from typing import List


class Item:
    def __init__(self, xs: List[int]) -> None:
        self.k = 1
        self.items: List[int] = list()


class Collector:
    def __init__(self) -> None:
        self.n = 0

    #@ requires len(xs) >= 0
    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, xs: List[int]) -> int:
        b = Item(xs)
        if b.items:
            return 1
        return 0
