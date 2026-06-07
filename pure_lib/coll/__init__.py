# pure_lib/coll — pure-Python collections module model
# Named 'coll' to avoid stdlib name clash.
#
# Contracts derived from library_reference/collections.rst.
# RST: "This module implements specialized container datatypes."
# RST: "deque, defaultdict, Counter, OrderedDict, namedtuple"
#
# Model: data structures as size-tracking classes.


""  # pycsl
#@ class invariant self._size >= 0
#@ class invariant self._maxlen >= 0
class Deque:
    """RST: 'Deques are a generalization of stacks and queues.
    Deques support thread-safe, memory efficient appends and pops.'"""

    def __init__(self):
        self._size = 0
        self._maxlen = 0

    #@ requires maxlen >= 0
    #@ ensures self._maxlen == maxlen
    #@ assigns self._maxlen
    def set_maxlen(self, maxlen: int) -> None:
        """Set maximum deque length (0 = unbounded)."""
        self._maxlen = maxlen

    #@ ensures self._size >= \old(self._size)
    #@ assigns self._size
    def append(self, item: int) -> None:
        """RST: 'Add x to the right side of the deque.'"""
        self._size = self._size + 1

    #@ ensures self._size >= \old(self._size)
    #@ assigns self._size
    def appendleft(self, item: int) -> None:
        """RST: 'Add x to the left side of the deque.'"""
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def pop(self) -> int:
        """RST: 'Remove and return an element from the right side.'"""
        self._size = self._size - 1
        return self._size

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def popleft(self) -> int:
        """RST: 'Remove and return an element from the left side.'"""
        self._size = self._size - 1
        return self._size

    #@ ensures \result == self._size
    #@ assigns \nothing
    def length(self) -> int:
        """Return current deque size."""
        return self._size

    #@ ensures self._size == 0
    #@ assigns self._size
    def clear(self) -> None:
        """RST: 'Remove all elements from the deque.'"""
        self._size = 0


""  # pycsl
#@ class invariant self._size >= 0
class Counter:
    """RST: 'A Counter is a dict subclass for counting hashable objects.'"""

    def __init__(self):
        self._size = 0

    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def increment(self, key: int) -> None:
        """Increment count for key."""
        self._size = self._size + 1

    #@ ensures \result == self._size
    #@ assigns \nothing
    def total(self) -> int:
        """RST: 'Return the total of all counts.'"""
        return self._size

    #@ ensures \result >= 0
    #@ assigns \nothing
    def most_common_count(self) -> int:
        """RST: 'Return a list of the n most common elements.'
        Returns count of elements returned."""
        return self._size


""  # pycsl
#@ class invariant self._size >= 0
class OrderedDict:
    """RST: 'Dictionary that remembers insertion order.'"""

    def __init__(self):
        self._size = 0

    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def setitem(self, key: int, val: int) -> None:
        """Add or update a key-value pair."""
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def popitem(self) -> int:
        """RST: 'Remove and return a (key, value) pair.'"""
        self._size = self._size - 1
        return self._size

    #@ ensures \result == self._size
    #@ assigns \nothing
    def length(self) -> int:
        """Number of entries."""
        return self._size
