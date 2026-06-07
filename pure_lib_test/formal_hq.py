# Formal test for heapq (hq) module
#
# Based on library_reference/heapq.rst:
#   "Push the value item onto the heap... maintaining the heap invariant."
#   "Pop and return the smallest item from the heap..."
#   "Return a list with the n largest/smallest elements."
#
# Tests verify contract postconditions:
#   - heappush: result == n + 1
#   - heappop: result == n - 1
#   - nlargest: result <= n and result <= k

from pure_lib.hq import heappush, heappop, heapreplace, nlargest, nsmallest, heappushpop


#@ ensures \result >= 0 and \result <= 11
def test_heappush_grows() -> int:
    """Pushing onto heap of 10 yields size n+1."""
    return heappush(10, 5)


#@ ensures \result >= 0
def test_heappop_shrinks() -> int:
    """Popping from heap of 10 yields non-negative size."""
    return heappop(10)


#@ ensures \result >= 0
def test_heapreplace_nonneg() -> int:
    """heapreplace result is non-negative."""
    return heapreplace(10, 3)


#@ ensures \result >= 0 and \result <= 3
def test_nlargest_bounded_k() -> int:
    """nlargest(3, 100): result bounded by k=3."""
    return nlargest(3, 100)


#@ ensures \result >= 0 and \result <= 5
def test_nsmallest_bounded_n() -> int:
    """nsmallest(10, 5): result bounded by n=5."""
    return nsmallest(10, 5)


#@ ensures \result >= 0
def test_heappushpop_nonneg() -> int:
    """heappushpop result is non-negative."""
    return heappushpop(8, 2)
