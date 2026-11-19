"""Helpers for corpus 7563 / 7567 (route #481): explicit `\trusted` defs of another module."""
from typing import List


#@ \trusted
def k_grow(xs: List[int]) -> int:
    xs.append(1)
    return 0


#@ \trusted
def k_store(xs: List[int]) -> int:
    xs[0] = 1
    return 0
