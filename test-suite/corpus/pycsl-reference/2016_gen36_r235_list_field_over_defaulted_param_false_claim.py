r"""Test 2016 — route #235 (expected FAIL): a `List[int]` field initialised over a parameter
bound from its KNOWN default (`n: int = 3`, `self.items = [0] * n`, constructed as `Item()`).
At base the collection arm ignored the bound initialiser and took the DEFINITE
`(Array.make 0 0)`, so `if b.items:` was decided False and `\result == 0` PROVED (CPython
returns 1); the field is now `any_array`.
"""
# pycsl-expected: FAIL
from typing import List

class Item:
    def __init__(self, n: int = 3) -> None:
        self.items: List[int] = [0] * n

class Collector:
    def __init__(self) -> None:
        self.c = 0

    #@ requires 0 <= k
    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, k: int) -> int:
        b = Item()
        if b.items:
            return 1
        return 0
