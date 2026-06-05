"""Formal driver for the bisect stub (the my_os_demo.py analog).

Exercises the real binary-search functions end-to-end: the insertion point is provably within
the searched range. Verifies with **zero** `\trusted`."""
from bisect import bisect_left, bisect_right, insort_left


#@ requires \length(a) >= 8
#@ ensures \result >= 0
#@ ensures \result <= 8
def demo_bisect_left(a: list, x: int) -> int:
    """The left insertion point in a[0:8] lands within [0, 8]."""
    return bisect_left(a, x, 0, 8)


#@ requires \length(a) >= 8
#@ ensures \result >= 0
#@ ensures \result <= 8
def demo_bisect_right(a: list, x: int) -> int:
    """The right insertion point in a[0:8] lands within [0, 8]."""
    return bisect_right(a, x, 0, 8)


#@ requires \length(a) >= 4
#@ ensures \result >= 0
#@ ensures \result <= 4
def demo_insort_left(a: list, x: int) -> int:
    """insort_left returns the computed left insertion point within [0, 4]."""
    return insort_left(a, x, 0, 4)
