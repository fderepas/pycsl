"""Formal driver for the heapq stub (the my_os_demo.py analog).

Exercises the priority-queue contracts end-to-end (the popped element relates to the pushed item
and the heap min/max). Verifies with **zero** `\trusted`. NOTE: the heap is modelled at the
return-value-contract level (`heap` is its opaque min/max); a full list-backed heap with the heap
invariant is a deeper, separate verification."""
from heapq import heappop, heappushpop, heapreplace, heappushpop_max


#@ requires h > 0
#@ ensures \result >= 0
def demo_heappop(h: int) -> int:
    """heappop yields a non-negative smallest element."""
    return heappop(h)


#@ ensures \result <= item
def demo_heappushpop(h: int, item: int) -> int:
    """heappushpop returns an element no larger than the pushed item."""
    return heappushpop(h, item)


#@ requires h <= item
#@ ensures \result <= item
def demo_heapreplace(h: int, item: int) -> int:
    """heapreplace pops the old min (<= item under the heap-min precondition)."""
    return heapreplace(h, item)


#@ ensures \result >= item
def demo_heappushpop_max(h: int, item: int) -> int:
    """heappushpop_max returns the larger of the item and the heap max."""
    return heappushpop_max(h, item)
