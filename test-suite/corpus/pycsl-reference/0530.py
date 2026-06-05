"""Test 0530 — itertools.chain length (A3, bounded eager).

`len(chain(a, b)) == len(a) + len(b)` for bounded lists. Fails today: chain has
no length model. Flips with a bounded-array chain under-approximation.
"""
_ = 0  # anchor
from typing import List
from itertools import chain

#@ requires \length(a) == 2
#@ requires \length(b) == 3
#@ ensures \result == 5
#@ assigns \nothing
def chain_len(a: List[int], b: List[int]) -> int:
    return len(list(chain(a, b)))
