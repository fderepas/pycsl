r"""Test 2018 — route #235 (expected FAIL): a `List[int]` field stored from a collection-builtin
call over a MODULE GLOBAL (`self.items = list(BASE)`, `BASE = [1, 2, 3]`). The literal-call
exemption meant for `list()` / `bytearray(4096)` let it keep the DEFINITE `(Array.make 0 0)`, so
`if b.items:` was decided False and `\result == 0` PROVED (CPython returns 1); the field is now
`any_array`. Control: 2015 (`list()` stays empty).
"""
# pycsl-expected: FAIL
from typing import List

BASE: List[int] = [1, 2, 3]


class Item:
    def __init__(self, k: int) -> None:
        self.k = k
        self.items: List[int] = list(BASE)


class Collector:
    def __init__(self) -> None:
        self.n = 0

    #@ requires 0 <= k
    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, k: int) -> int:
        b = Item(k)
        if b.items:
            return 1
        return 0
