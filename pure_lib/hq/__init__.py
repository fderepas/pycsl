# pure_lib/hq — pure-Python heapq module model
# Named 'hq' to avoid stdlib name clash.
#
# Models heap operations with the min-heap invariant.
# Key property: heap[0] is always the minimum element.


#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures \result <= n + 1
def heappush(n: int, item: int) -> int:
    """Push item onto heap of size n. Returns new size = n+1."""
    return n + 1


#@ requires n >= 1
#@ ensures \result >= 0
#@ ensures \result == n - 1
def heappop(n: int) -> int:
    """Pop smallest item from heap of size n. Returns new size = n-1."""
    return n - 1


#@ requires n >= 1
#@ ensures \result >= 0
#@ ensures \result == n
def heapreplace(n: int, item: int) -> int:
    """Pop and push in one operation. Size unchanged."""
    return n


#@ requires n >= 0
#@ ensures \result == n
def heapify(n: int) -> int:
    """Transform list of size n into a heap in-place. Size unchanged."""
    return n


#@ requires n >= 0
#@ requires k >= 0
#@ ensures \result >= 0
#@ ensures \result <= n
#@ ensures \result <= k
def nlargest(k: int, n: int) -> int:
    """Return k largest elements from collection of size n."""
    if k <= n:
        return k
    return n


#@ requires n >= 0
#@ requires k >= 0
#@ ensures \result >= 0
#@ ensures \result <= n
#@ ensures \result <= k
def nsmallest(k: int, n: int) -> int:
    """Return k smallest elements from collection of size n."""
    if k <= n:
        return k
    return n


#@ requires n >= 1
#@ ensures \result >= 0
#@ ensures \result == n
def heappushpop(n: int, item: int) -> int:
    """Push then pop. Faster than heappush+heappop. Size unchanged."""
    return n
