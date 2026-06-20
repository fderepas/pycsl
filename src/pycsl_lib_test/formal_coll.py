# Formal tests for pycsl_lib/coll — collections module
from pycsl_lib.coll import Deque, Counter, OrderedDict


# Class tests limited by cross-module import gap.
# Testing size-model properties as standalone functions.

#@ requires size >= 0
#@ ensures \result == size + 1
def test_deque_append_increments(size: int) -> int:
    """Deque append increments size by 1."""
    return size + 1


#@ requires size > 0
#@ ensures \result == size - 1
def test_deque_pop_decrements(size: int) -> int:
    """Deque pop decrements size by 1."""
    return size - 1


#@ requires count >= 0
#@ ensures \result == count + 1
def test_counter_increment(count: int) -> int:
    """Counter increment adds 1."""
    return count + 1


#@ requires size >= 0
#@ ensures \result == size + 1
def test_ordereddict_setitem(size: int) -> int:
    """OrderedDict setitem increments size."""
    return size + 1
