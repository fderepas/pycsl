"""Test 0548 — itertools.islice length (A3-residual).

`len(list(islice(a, n))) == min(len(a), n)` — a bounded slice yields up to `n`
elements (inline `min` via if-then-else, no MinMax import). With |a|=5 and n=3
the slice has 3 elements. Flips when `_iter_len_expr` handles `islice`.
"""
_ = 0  # anchor
from typing import List
from itertools import islice


#@ requires \length(a) == 5
#@ ensures \result == 3
#@ assigns \nothing
def islice_len(a: List[int]) -> int:
    return len(list(islice(a, 3)))
