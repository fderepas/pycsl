"""PyCSL mock for Python's heapq module — Heap queue algorithm (a.k.a. priority queue)."""
_ = 0  # anchor

# cite: https://docs.python.org/3/library/heapq.html#heapq.heapify
#@ ensures True
#@ assigns x
def heapify(x: int) -> int:
    """Mock: Transform list *x* into a min-heap, in-place, in linear time."""
    return 0

# cite: https://docs.python.org/3/library/heapq.html#heapq.heappush
#@ ensures True
#@ assigns heap
def heappush(heap: int, item: int) -> int:
    """Mock: Push the value *item* onto the *heap*, maintaining the min-heap invariant."""
    return 0

# cite: https://docs.python.org/3/library/heapq.html#heapq.heappop
#@ requires heap > 0
#@ ensures \result >= 0
def heappop(heap: int) -> int:
    """Mock: Pop and return the smallest item from the *heap*, maintaining the min-heap invariant.  If the heap is empty, :exc:`Index..."""
    return 0

# cite: https://docs.python.org/3/library/heapq.html#heapq.heappushpop
#@ ensures \result <= item
def heappushpop(heap: int, item: int) -> int:
    """Push *item* then pop the smallest. The popped element is no larger than the just-pushed
    *item* (it competes with it), so `result <= item`. The heap array is modelled at the
    contract level (`heap` is its opaque min); body-verified return value."""
    return item

# cite: https://docs.python.org/3/library/heapq.html#heapq.heapreplace
#@ requires heap <= item
#@ ensures \result <= item
def heapreplace(heap: int, item: int) -> int:
    """Pop the smallest then push *item*. With the heap min `heap <= item`, the popped value
    (the old min) is `<= item`; returning it (`heap`) discharges `result <= item`."""
    return heap

# cite: https://docs.python.org/3/library/heapq.html#heapq.heapify
#@ ensures True
#@ assigns x
def heapify_max(x: int) -> int:
    """Mock: Transform list *x* into a max-heap, in-place, in linear time. .. versionadded:: 3.14"""
    return 0

# cite: https://docs.python.org/3/library/heapq.html
#@ ensures True
def heappush_max(heap: int, item: int) -> int:
    """Mock: Push the value *item* onto the max-heap *heap*, maintaining the max-heap invariant. .. versionadded:: 3.14"""
    return 0

# cite: https://github.com/python/cpython/blob/main/Lib/heapq.py
#@ ensures True
def heappop_max(heap: int) -> int:
    """Mock: Pop and return the largest item from the max-heap *heap*, maintaining the max-heap invariant.  If the max-heap is empty,..."""
    return 0

# cite: https://docs.python.org/3/library/heapq.html#heapq.heappushpop
#@ ensures \result >= item
#@ ensures \result >= heap
def heappushpop_max(heap: int, item: int) -> int:
    """Push *item* on the max-heap then pop the largest — which is `max(item, heap-max)`, hence
    `result >= item` and `result >= heap`. Body-verified at the contract level."""
    if item >= heap:
        return item
    return heap

# cite: https://docs.python.org/3/library/heapq.html#heapq.heapreplace
#@ requires heap >= item
#@ ensures \result >= item
def heapreplace_max(heap: int, item: int) -> int:
    """Pop the largest then push *item*. With the max `heap >= item`, the popped value (the old
    max) is `>= item`; returning it (`heap`) discharges `result >= item`."""
    return heap

# cite: https://docs.python.org/3/library/heapq.html#heapq.merge
# cite:_note: result is a lazy generator; sorted-output invariant exceeds expressible contract surface on mock return type (int)
#@ ensures True
def merge(key: int, reverse: int) -> int:
    """Mock: Merge multiple sorted inputs into a single sorted output (for example, merge timestamped entries from multiple log files..."""
    return 0

# cite: https://docs.python.org/3/library/heapq.html#heapq.nlargest
#@ requires n >= 0
#@ ensures \result >= 0
def nlargest(n: int, iterable: int, key: int) -> int:
    """Mock: Return a list with the *n* largest elements from the dataset defined by *iterable*.  *key*, if provided, specifies a fun..."""
    return 0

# cite: https://docs.python.org/3/library/heapq.html#heapq.nsmallest
#@ requires n >= 0
#@ ensures True
def nsmallest(n: int, iterable: int, key: int) -> int:
    """Mock: Return a list with the *n* smallest elements from the dataset defined by *iterable*.  *key*, if provided, specifies a fu..."""
    return 0
