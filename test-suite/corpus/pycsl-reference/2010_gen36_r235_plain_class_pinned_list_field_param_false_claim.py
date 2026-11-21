r"""Test 2010 — route #235 (expected FAIL): a PLAIN class (`self.items: List[str] = xs`) that
is PINNED by a `-> List[Item]` function, so its list field is the pure `seq string`. At base
`Item(1, xs)` dropped `xs` for `Seq.empty` and `len(b.items) == 0` PROVED (CPython returns 3).
"""
# pycsl-expected: FAIL
from typing import List


class Item:
    def __init__(self, k: int, xs: List[str]) -> None:
        self.k = k
        self.items: List[str] = xs


#@ \trusted
#@ requires 0 <= k
#@ assigns \nothing
def none(k: int) -> List[Item]:
    return []


#@ requires len(xs) == 3
#@ ensures \result == 0
#@ assigns \nothing
def count(xs: List[str]) -> int:
    b = Item(1, xs)
    return len(b.items)
