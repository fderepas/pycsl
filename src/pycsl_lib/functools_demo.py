"""Formal driver for the functools stub (the my_os_demo.py analog).

Exercises the real left-fold `reduce` (accumulator monotonicity) and the identity/sentinel
utilities. Verifies with **zero** `\trusted`."""
from functools import reduce, total_ordering, partial


#@ requires n >= 0
#@ requires \length(vals) >= n
#@ requires \forall i; 0 <= i and i < n ==> vals[i] >= 0
#@ requires init >= 0
#@ ensures \result >= init
def demo_reduce(vals: list, n: int, init: int) -> int:
    """The sum-fold of non-negative values never drops below the initializer."""
    return reduce(0, vals, n, init)


#@ ensures \result == c
def demo_total_ordering(c: int) -> int:
    """@total_ordering returns the class unchanged."""
    return total_ordering(c)


#@ ensures \result >= 0
def demo_partial(f: int) -> int:
    """partial() yields a non-negative sentinel."""
    return partial(f)
