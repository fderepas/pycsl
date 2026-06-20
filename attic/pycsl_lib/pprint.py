"""PyCSL mock for Python's pprint module — Data pretty printer."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def pp(object: int, stream: int, indent: int, width: int, depth: int, __compact: int, sort_dicts: int) -> int:
    """Mock: Prints the formatted representation of *object*, followed by a newline. This function may be used in the interactive int..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def pprint(object: int, stream: int, indent: int, width: int, depth: int, __compact: int, sort_dicts: int) -> int:
    """Mock: Alias for :func:`~pprint.pp` with *sort_dicts* set to ``True`` by default, which would automatically sort the dictionari..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pformat(object: int, indent: int, width: int, depth: int, __compact: int, sort_dicts: int, underscore_numbers: int) -> int:
    """Mock: Return the formatted representation of *object* as a string.  *indent*, *width*, *depth*, *compact*, *sort_dicts* and *u..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isreadable(object: int) -> int:
    """Mock: .. index:: pair: built-in function; eval Determine if the formatted representation of *object* is 'readable', or can be ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isrecursive(object: int) -> int:
    """Mock: Determine if *object* requires a recursive representation.  This function is subject to the same limitations as noted in..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def saferepr(object: int) -> int:
    """Mock: Return a string representation of *object*, protected against recursion in some common data structures, namely instances..."""
    return 0
