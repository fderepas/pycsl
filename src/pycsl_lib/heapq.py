"""PyCSL mock for Python's heapq module — Heap queue algorithm (a.k.a. priority queue)."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.heapify
#@ ensures True
#@ assigns x
def heapify(x: int) -> int:
    """Mock: Transform list *x* into a min-heap, in-place, in linear time."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.heappush
#@ ensures True
#@ assigns heap
def heappush(heap: int, item: int) -> int:
    """Mock: Push the value *item* onto the *heap*, maintaining the min-heap invariant."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.heappop
#@ requires heap > 0
#@ ensures \result >= 0
def heappop(heap: int) -> int:
    """Mock: Pop and return the smallest item from the *heap*, maintaining the min-heap invariant.  If the heap is empty, :exc:`Index..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.heappushpop
#@ ensures \result <= item
def heappushpop(heap: int, item: int) -> int:
    """Mock: Push *item* on the heap, then pop and return the smallest item from the *heap*.  The combined action runs more efficient..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.heapreplace
#@ requires heap <= item
#@ ensures \result <= item
def heapreplace(heap: int, item: int) -> int:
    """Mock: Pop and return the smallest item from the *heap*, and also push the new *item*. The heap size doesn't change. If the hea..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.heapify
#@ ensures True
#@ assigns x
def heapify_max(x: int) -> int:
    """Mock: Transform list *x* into a max-heap, in-place, in linear time. .. versionadded:: 3.14"""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html
#@ ensures True
def heappush_max(heap: int, item: int) -> int:
    """Mock: Push the value *item* onto the max-heap *heap*, maintaining the max-heap invariant. .. versionadded:: 3.14"""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/heapq.py
#@ ensures True
def heappop_max(heap: int) -> int:
    """Mock: Pop and return the largest item from the max-heap *heap*, maintaining the max-heap invariant.  If the max-heap is empty,..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.heappushpop
#@ ensures \result >= item
#@ ensures \result >= heap
def heappushpop_max(heap: int, item: int) -> int:
    """Mock: Push *item* on the max-heap *heap*, then pop and return the largest item from *heap*. The combined action runs more effi..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.heapreplace
#@ requires heap >= item
#@ ensures \result >= item
def heapreplace_max(heap: int, item: int) -> int:
    """Mock: Pop and return the largest item from the max-heap *heap* and also push the new *item*. The max-heap size doesn't change...."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.merge
# cite:_note: result is a lazy generator; sorted-output invariant exceeds expressible contract surface on mock return type (int)
#@ ensures True
def merge(key: int, reverse: int) -> int:
    """Mock: Merge multiple sorted inputs into a single sorted output (for example, merge timestamped entries from multiple log files..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.nlargest
#@ requires n >= 0
#@ ensures \result >= 0
def nlargest(n: int, iterable: int, key: int) -> int:
    """Mock: Return a list with the *n* largest elements from the dataset defined by *iterable*.  *key*, if provided, specifies a fun..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/heapq.html#heapq.nsmallest
#@ requires n >= 0
#@ ensures True
def nsmallest(n: int, iterable: int, key: int) -> int:
    """Mock: Return a list with the *n* smallest elements from the dataset defined by *iterable*.  *key*, if provided, specifies a fu..."""
    return 0
