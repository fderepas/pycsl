r"""Test 1556 - ROUTE #162 (gen #29): `heapq.heapify(xs)` on a list PARAMETER in an `assigns \nothing` function; the dotted call became an abstract op with no `writes`, and a caller proved `xs[0]` unchanged (5) while CPython reorders it to 1. A standard-library argument mutator is now refused.
"""
# pycsl-expected: FAIL
import heapq
from typing import List
_ = 0  # anchor


#@ requires len(xs) == 2
#@ assigns \nothing
def f(xs: List[int]) -> None:
    heapq.heapify(xs)


#@ requires len(xs) == 2 and xs[0] == 5 and xs[1] == 1
#@ ensures \result == 5
def probe(xs: List[int]) -> int:
    f(xs)
    return xs[0]

