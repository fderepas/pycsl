r"""Test 2014 — route #235 (expected FAIL): the DICT arm of 2013 —
`self.items = {k: v for k, v in xs.items()}` over a parameter with `1 in xs`. At base the field
was the DEFINITE empty map `(const None)`, `1 in b.items` was decided False and `\result == 0`
PROVED (CPython returns 1); the field is now the polymorphic unconstrained `any_map`.
"""
# pycsl-expected: FAIL
from typing import Dict


class Item:
    def __init__(self, xs: Dict[int, int]) -> None:
        self.k = 1
        self.items: Dict[int, int] = {k: v for k, v in xs.items()}


class Collector:
    def __init__(self) -> None:
        self.n = 0

    #@ requires 1 in xs
    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, xs: Dict[int, int]) -> int:
        b = Item(xs)
        if 1 in b.items:
            return 1
        return 0
