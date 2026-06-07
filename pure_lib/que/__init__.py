# pure_lib/que — pure-Python queue module model
# Named 'que' to avoid stdlib name clash.
#
# Contracts derived from library_reference/queue.rst.
# RST: "The queue module implements multi-producer, multi-consumer queues."
# RST: "Queue, LifoQueue, PriorityQueue"
#
# Model: track size and maxsize. Thread-safety not modeled
# (requires concurrency theory).


""  # pycsl
#@ class invariant self._size >= 0
#@ class invariant self._maxsize >= 0
class Queue:
    """RST: 'Constructor for a FIFO queue. maxsize is an integer that
    sets the upperbound limit on the number of items.'"""

    def __init__(self):
        self._size = 0
        self._maxsize = 0

    #@ requires maxsize >= 0
    #@ ensures self._maxsize == maxsize
    #@ assigns self._maxsize
    def set_maxsize(self, maxsize: int) -> None:
        """Configure the queue's maximum size (0 = unlimited)."""
        self._maxsize = maxsize

    #@ requires self._maxsize == 0 or self._size < self._maxsize
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def put(self, item: int) -> None:
        """RST: 'Put an item into the queue.'
        Requires space available (or unlimited)."""
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ ensures \result >= 0
    #@ assigns self._size
    def get(self) -> int:
        """RST: 'Remove and return an item from the queue.'
        Requires non-empty queue."""
        self._size = self._size - 1
        return self._size

    #@ ensures \result == self._size
    #@ assigns \nothing
    def qsize(self) -> int:
        """RST: 'Return the approximate size of the queue.'"""
        return self._size

    #@ ensures \result == 1 or \result == 0
    #@ ensures self._size == 0 ==> \result == 1
    #@ ensures self._size > 0 ==> \result == 0
    #@ assigns \nothing
    def empty(self) -> int:
        """RST: 'Return True if the queue is empty.'"""
        if self._size == 0:
            return 1
        return 0

    #@ ensures \result == 1 or \result == 0
    #@ ensures (self._maxsize > 0 and self._size >= self._maxsize) ==> \result == 1
    #@ assigns \nothing
    def full(self) -> int:
        """RST: 'Return True if the queue is full.'"""
        if self._maxsize > 0 and self._size >= self._maxsize:
            return 1
        return 0


""  # pycsl
#@ class invariant self._size >= 0
#@ class invariant self._maxsize >= 0
class LifoQueue:
    """RST: 'A variant of Queue that retrieves most recently added entries first (LIFO).'"""

    def __init__(self):
        self._size = 0
        self._maxsize = 0

    #@ requires maxsize >= 0
    #@ ensures self._maxsize == maxsize
    #@ assigns self._maxsize
    def set_maxsize(self, maxsize: int) -> None:
        """Configure max size."""
        self._maxsize = maxsize

    #@ requires self._maxsize == 0 or self._size < self._maxsize
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def push(self, item: int) -> None:
        """RST: 'Put an item into the queue.' LIFO push."""
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def pop(self) -> int:
        """RST: 'Remove and return an item.' LIFO pop."""
        self._size = self._size - 1
        return self._size

    #@ ensures \result == self._size
    #@ assigns \nothing
    def qsize(self) -> int:
        """Return queue size."""
        return self._size


""  # pycsl
#@ class invariant self._size >= 0
#@ class invariant self._maxsize >= 0
class PriorityQueue:
    """RST: 'A variant of Queue that retrieves entries in priority order (lowest first).'"""

    def __init__(self):
        self._size = 0
        self._maxsize = 0

    #@ requires maxsize >= 0
    #@ ensures self._maxsize == maxsize
    #@ assigns self._maxsize
    def set_maxsize(self, maxsize: int) -> None:
        """Configure max size."""
        self._maxsize = maxsize

    #@ requires self._maxsize == 0 or self._size < self._maxsize
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def put(self, priority: int) -> None:
        """RST: 'Put an item with priority into the queue.'"""
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def get(self) -> int:
        """RST: 'Remove and return the lowest priority item.'"""
        self._size = self._size - 1
        return self._size

    #@ ensures \result == self._size
    #@ assigns \nothing
    def qsize(self) -> int:
        """Return queue size."""
        return self._size
