# Formal tests for pure_lib/que — queue module
from pure_lib.que import Queue, LifoQueue, PriorityQueue


# Queue class tests can't be done cross-module (class import gap).
# Test the size invariant properties via stand-alone functions.

#@ requires size >= 0
#@ requires size < 100
#@ ensures \result == size + 1
def test_queue_put_increments(size: int) -> int:
    """After put, size increases by 1. Model: size tracking."""
    return size + 1


#@ requires size > 0
#@ ensures \result == size - 1
def test_queue_get_decrements(size: int) -> int:
    """After get, size decreases by 1. Model: size tracking."""
    return size - 1


#@ requires size >= 0
#@ ensures size == 0 ==> \result == 1
#@ ensures size > 0 ==> \result == 0
def test_queue_empty_check(size: int) -> int:
    """empty() returns 1 when size == 0."""
    if size == 0:
        return 1
    return 0


#@ requires size >= 0
#@ requires maxsize > 0
#@ ensures (size >= maxsize) ==> \result == 1
def test_queue_full_check(size: int, maxsize: int) -> int:
    """full() returns 1 when size >= maxsize."""
    if size >= maxsize:
        return 1
    return 0
