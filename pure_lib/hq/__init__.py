# pure_lib/hq — pure-Python heapq module model
# Named 'hq' to avoid stdlib name clash.
#
# Contracts derived from library_reference/heapq.rst.
# RST: "Push the value item onto the heap, maintaining the min-heap invariant."
# RST: "Pop and return the smallest item from the heap."
# RST: "The heap size doesn't change" (heapreplace).
# RST: "Return a list with the n largest/smallest elements."


#@ requires n >= 0
#@ ensures \result == n + 1
def heappush(n: int, item: int) -> int:
    """RST: 'Push the value item onto the heap.' Size grows by exactly 1."""
    return n + 1


#@ requires n >= 1
#@ ensures \result == n - 1
def heappop(n: int) -> int:
    """RST: 'Pop and return the smallest item.' Size shrinks by exactly 1.
    Requires non-empty heap (RST: 'If the heap is empty, IndexError is raised.')"""
    return n - 1


#@ requires n >= 1
#@ ensures \result == n
def heapreplace(n: int, item: int) -> int:
    """RST: 'Pop and return the smallest item, and also push the new item.
    The heap size doesn't change.' Size is exactly preserved."""
    return n


#@ requires n >= 0
#@ ensures \result == n
def heapify(n: int) -> int:
    """RST: 'Transform list into a heap, in-place.' Size unchanged."""
    return n


#@ requires n >= 0
#@ requires k >= 0
#@ ensures \result >= 0
#@ ensures \result <= n
#@ ensures \result <= k
#@ ensures k <= n ==> \result == k
#@ ensures n < k ==> \result == n
def nlargest(k: int, n: int) -> int:
    """RST: 'Return a list with the n largest elements.'
    Equivalent to sorted(iterable, reverse=True)[:n] → result = min(k, n)."""
    if k <= n:
        return k
    return n


#@ requires n >= 0
#@ requires k >= 0
#@ ensures \result >= 0
#@ ensures \result <= n
#@ ensures \result <= k
#@ ensures k <= n ==> \result == k
#@ ensures n < k ==> \result == n
def nsmallest(k: int, n: int) -> int:
    """RST: 'Return a list with the n smallest elements.'
    Equivalent to sorted(iterable)[:n] → result = min(k, n)."""
    if k <= n:
        return k
    return n


#@ requires n >= 1
#@ ensures \result == n
def heappushpop(n: int, item: int) -> int:
    """RST: 'Push item on the heap, then pop and return the smallest item.'
    Combined action: size unchanged (push +1, pop -1 = net 0)."""
    return n


#@ requires n >= 0
#@ requires \length(heap) == n
#@ ensures \result == n
def heapify_max(heap: list, n: int) -> int:
    """RST: 'Transform list into a max-heap, in-place.' Size unchanged."""
    return n


#@ requires n >= 0
#@ requires \length(heap) == n
#@ ensures \result == n + 1
def heappush_max(heap: list, n: int, item: int) -> int:
    """RST: 'Push the value item onto the max-heap.' Size grows by exactly 1."""
    return n + 1


#@ requires n >= 1
#@ requires \length(heap) == n
#@ ensures \result == n - 1
def heappop_max(heap: list, n: int) -> int:
    """RST: 'Pop and return the largest item.' Size shrinks by exactly 1.
    Requires non-empty heap."""
    return n - 1


#@ requires n >= 1
#@ requires \length(heap) == n
#@ ensures \result == n
def heappushpop_max(heap: list, n: int, item: int) -> int:
    """RST: 'Push item on the max-heap, then pop and return the largest item.'
    Combined action leaves the heap size unchanged."""
    return n


#@ requires n >= 1
#@ requires \length(heap) == n
#@ ensures \result == n
def heapreplace_max(heap: list, n: int, item: int) -> int:
    """RST: 'Pop and return the largest item, and also push the new item.'
    The max-heap size is exactly preserved."""
    return n
