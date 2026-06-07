# Formal test for heapq (hq) module — universally quantified
#
# Based on library_reference/heapq.rst:
#   "Push the value item onto the heap." → size grows by exactly 1.
#   "Pop and return the smallest item." → size shrinks by exactly 1.
#   "The heap size doesn't change." (heapreplace, heappushpop)
#   "Return a list with the n largest/smallest elements."
#    → equivalent to sorted(...)[:n] → result = min(k, n).

from pure_lib.hq import heappush, heappop, heapreplace, nlargest, nsmallest, heappushpop


#@ requires n >= 0 and n < 2147483647
#@ requires item >= 0
#@ ensures \result == n + 1
def test_heappush_exact(n: int, item: int) -> int:
    """heappush(n, item) == n+1 for all n. Push adds exactly 1."""
    return heappush(n, item)


#@ requires n >= 1 and n < 2147483647
#@ ensures \result == n - 1
def test_heappop_exact(n: int) -> int:
    """heappop(n) == n-1 for all n >= 1. Pop removes exactly 1."""
    return heappop(n)


#@ requires n >= 1 and n < 2147483647
#@ requires item >= 0
#@ ensures \result == n
def test_heapreplace_same(n: int, item: int) -> int:
    """heapreplace(n, item) == n for all n >= 1. Size unchanged."""
    return heapreplace(n, item)


#@ requires k >= 0 and k < 2147483647
#@ requires n >= 0 and n < 2147483647
#@ ensures \result >= 0 and \result <= k and \result <= n
def test_nlargest_bounded(k: int, n: int) -> int:
    """nlargest(k, n) <= min(k, n) for all k, n."""
    return nlargest(k, n)


#@ requires k >= 0 and k < 2147483647
#@ requires n >= 0 and n < 2147483647
#@ ensures \result >= 0 and \result <= k and \result <= n
def test_nsmallest_bounded(k: int, n: int) -> int:
    """nsmallest(k, n) <= min(k, n) for all k, n."""
    return nsmallest(k, n)


#@ requires n >= 1 and n < 2147483647
#@ requires item >= 0
#@ ensures \result == n
def test_heappushpop_same(n: int, item: int) -> int:
    """heappushpop(n, item) == n for all n >= 1. Size unchanged."""
    return heappushpop(n, item)
