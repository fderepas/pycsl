r"""Test 2013 — route #235 (expected FAIL): a `List[int]` field whose `__init__` store is a
NON-CAPTURED expression over a parameter (`self.items = list(xs)`). The capture rule needs every
free name to be a parameter (`list` is not), so no binder fires and the field fell to the DEFINITE
`(Array.make 0 0)`: with `len(xs) == 3`, `if b.items:` was decided False and `\result == 0`
PROVED (CPython returns 1). The field now joins the collection-unknown channel (`any_array`).
"""
# pycsl-expected: FAIL
from typing import List


class Item:
    def __init__(self, xs: List[int]) -> None:
        self.k = 1
        self.items: List[int] = list(xs)


class Collector:
    def __init__(self) -> None:
        self.n = 0

    #@ requires len(xs) == 3
    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, xs: List[int]) -> int:
        b = Item(xs)
        if b.items:
            return 1
        return 0
