# Formal test for heapq (hq) module
#
# Based on library_reference/heapq.rst:
#   "Push the value item onto the heap." → size grows by exactly 1.
#   "Pop and return the smallest item." → size shrinks by exactly 1.
#   "The heap size doesn't change." (heapreplace, heappushpop)
#   "Return a list with the n largest/smallest elements."
#    → equivalent to sorted(...)[:n] → result = min(k, n).

from pure_lib.hq import heappush, heappop, heapreplace, nlargest, nsmallest, heappushpop


#@ ensures \result == 11
def test_heappush_exact() -> int:
    """Push onto heap of 10 → size 11. Exact from RST."""
    return heappush(10, 5)


#@ ensures \result == 9
def test_heappop_exact() -> int:
    """Pop from heap of 10 → size 9. Exact from RST."""
    return heappop(10)


#@ ensures \result == 10
def test_heapreplace_same() -> int:
    """RST: 'The heap size doesn't change.' heapreplace(10) == 10."""
    return heapreplace(10, 3)


#@ ensures \result >= 0 and \result <= 3
def test_nlargest_bounded_k() -> int:
    """RST: 'sorted(iterable, reverse=True)[:n]' → bounded by k."""
    return nlargest(3, 100)


#@ ensures \result >= 0 and \result <= 5
def test_nsmallest_bounded_n() -> int:
    """RST: 'sorted(iterable)[:n]' → bounded by n."""
    return nsmallest(10, 5)


#@ ensures \result == 8
def test_heappushpop_same() -> int:
    """RST: 'Push then pop.' Net size unchanged: heappushpop(8) == 8."""
    return heappushpop(8, 2)
