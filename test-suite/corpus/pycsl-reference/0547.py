"""Test 0547 — itertools.product length (A3-residual).

`len(list(product(a, b))) == len(a) * len(b)` — the cartesian product of bounded
lists. With |a|=2 and |b|=3 the product has 6 tuples. Bounded/eager model
(lazy product out of scope). Flips when `_iter_len_expr` handles `product`.
"""
_ = 0  # anchor
from typing import List
from itertools import product


#@ requires \length(a) == 2
#@ requires \length(b) == 3
#@ ensures \result == 6
#@ assigns \nothing
def product_len(a: List[int], b: List[int]) -> int:
    return len(list(product(a, b)))
