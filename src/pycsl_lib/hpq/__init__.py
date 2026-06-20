# Pure model for heapq — heap queue algorithm
# Models heap as a size-tracked abstract structure.
# Invariant: size >= 0 at all times.

""" # pycsl"""


#@ class invariant self._size >= 0
class Heap:
    """Abstract min-heap tracking size and minimum element."""

    #@ ensures self._size == 0
    #@ ensures self._min == 0
    def __init__(self) -> None:
        self._size: int = 0
        self._min: int = 0

    #@ requires self._size >= 0
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size, self._min
    def push(self, item: int) -> None:
        """Push item onto heap."""
        if self._size == 0:
            self._min = item
        else:
            if item < self._min:
                self._min = item
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ ensures \result == \old(self._min)
    #@ assigns self._size, self._min
    def pop(self) -> int:
        """Pop and return smallest item."""
        result: int = self._min
        self._size = self._size - 1
        self._min = 0
        return result


#@ requires size >= 0
#@ ensures \result == size + 1
def heappush(size: int, item: int) -> int:
    """Model: heap push increments size."""
    return size + 1


#@ requires size > 0
#@ ensures \result == size - 1
def heappop(size: int) -> int:
    """Model: heap pop decrements size."""
    return size - 1


#@ requires size > 0
#@ ensures \result == size
def heappushpop(size: int, item: int) -> int:
    """Model: pushpop keeps size constant."""
    return size


#@ requires size > 0
#@ ensures \result == size
def heapreplace(size: int, item: int) -> int:
    """Model: heapreplace keeps size constant."""
    return size


#@ requires size >= 0
#@ ensures \result == size
def heapify(size: int) -> int:
    """Model: heapify preserves size."""
    return size


#@ requires n >= 0
#@ requires n <= size
#@ ensures \result == n
def nsmallest(n: int, size: int) -> int:
    """Return n smallest elements (count model)."""
    return n


#@ requires n >= 0
#@ requires n <= size
#@ ensures \result == n
def nlargest(n: int, size: int) -> int:
    """Return n largest elements (count model)."""
    return n
