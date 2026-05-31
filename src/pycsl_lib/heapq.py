"""PyCSL mock for Python's heapq module — Heap queue algorithm (a.k.a. priority queue)."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def heapify(x: int) -> int:
    """Mock: Transform list *x* into a min-heap, in-place, in linear time."""
    return 0

#@ \trusted
#@ ensures \result == 0
def heappush(heap: int, item: int) -> int:
    """Mock: Push the value *item* onto the *heap*, maintaining the min-heap invariant."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def heappop(heap: int) -> int:
    """Mock: Pop and return the smallest item from the *heap*, maintaining the min-heap invariant.  If the heap is empty, :exc:`Index..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def heappushpop(heap: int, item: int) -> int:
    """Mock: Push *item* on the heap, then pop and return the smallest item from the *heap*.  The combined action runs more efficient..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def heapreplace(heap: int, item: int) -> int:
    """Mock: Pop and return the smallest item from the *heap*, and also push the new *item*. The heap size doesn't change. If the hea..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def heapify_max(x: int) -> int:
    """Mock: Transform list *x* into a max-heap, in-place, in linear time. .. versionadded:: 3.14"""
    return 0

#@ \trusted
#@ ensures \result == 0
def heappush_max(heap: int, item: int) -> int:
    """Mock: Push the value *item* onto the max-heap *heap*, maintaining the max-heap invariant. .. versionadded:: 3.14"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def heappop_max(heap: int) -> int:
    """Mock: Pop and return the largest item from the max-heap *heap*, maintaining the max-heap invariant.  If the max-heap is empty,..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def heappushpop_max(heap: int, item: int) -> int:
    """Mock: Push *item* on the max-heap *heap*, then pop and return the largest item from *heap*. The combined action runs more effi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def heapreplace_max(heap: int, item: int) -> int:
    """Mock: Pop and return the largest item from the max-heap *heap* and also push the new *item*. The max-heap size doesn't change...."""
    return 0

#@ \trusted
#@ ensures \result == 0
def merge(key: int, reverse: int) -> int:
    """Mock: Merge multiple sorted inputs into a single sorted output (for example, merge timestamped entries from multiple log files..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nlargest(n: int, iterable: int, key: int) -> int:
    """Mock: Return a list with the *n* largest elements from the dataset defined by *iterable*.  *key*, if provided, specifies a fun..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nsmallest(n: int, iterable: int, key: int) -> int:
    """Mock: Return a list with the *n* smallest elements from the dataset defined by *iterable*.  *key*, if provided, specifies a fu..."""
    return 0
