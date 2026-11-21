r"""Test 2017 — route #235 (expected FAIL): a dataclass `List[int]` field whose OMITTED actual
runs a NON-BUILTIN `default_factory` (`lambda: [1, 2, 3]`). At base the field took the
DEFINITE `(Array.make 0 0)`, so `if b.items:` was decided False and `\result == 0` PROVED
(CPython returns 1); the field is now `any_array`. A bare `default_factory=list` keeps the
faithful empty value (2011).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List

@dataclass
class Item:
    k: int
    items: List[int] = field(default_factory=lambda: [1, 2, 3])

class Collector:
    def __init__(self) -> None:
        self.c = 0

    #@ requires 0 <= k
    #@ ensures \result == 0
    #@ assigns \nothing
    def count(self, k: int) -> int:
        b = Item(1)
        if b.items:
            return 1
        return 0
