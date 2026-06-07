# Formal tests for pure_lib/hpq — heapq module
from pure_lib.hpq import heappush, heappop, heappushpop, heapreplace, heapify, nsmallest


#@ requires size >= 0
#@ ensures \result == size + 1
def test_push_increments(size: int) -> int:
    """Push increments heap size."""
    return heappush(size, 42)


#@ requires size > 0
#@ ensures \result == size - 1
def test_pop_decrements(size: int) -> int:
    """Pop decrements heap size."""
    return heappop(size)


#@ requires size > 0
#@ ensures \result == size
def test_pushpop_stable(size: int) -> int:
    """Pushpop keeps size constant."""
    return heappushpop(size, 10)


#@ requires size >= 0
#@ ensures \result == size
def test_heapify_preserves(size: int) -> int:
    """Heapify preserves size."""
    return heapify(size)


#@ requires n >= 0
#@ requires n <= size
#@ ensures \result == n
def test_nsmallest_count(n: int, size: int) -> int:
    """nsmallest returns exactly n elements."""
    return nsmallest(n, size)
