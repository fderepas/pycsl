"""PyCSL mock for Python's itertools module.

Provides trusted stubs for creating iterators for efficient looping:
combinations, permutations, infinite iteration, and iteration utilities.
"""
_ = 0  # anchor

# ── Combinatorics ─────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.combinations
#@ requires r >= 0
#@ ensures \result >= 0
def combinations(iterable: int, r: int) -> int:
    """Mock: return successive r-length tuples of elements from the iterable."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.permutations
#@ requires iterable >= 0
#@ requires r >= 0
#@ requires r <= iterable
#@ ensures \result >= 0
def permutations(iterable: int, r: int) -> int:
    """Mock: return successive r-length permutations of elements from the iterable."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.product
#@ requires repeat >= 0
#@ ensures True
def product(*iterables: int, repeat: int) -> int:
    """Mock: return cartesian product of input iterables."""
    return 0

# ── Iteration ──────────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.chain
#@ ensures True
def chain(*iterables: int) -> int:
    """Mock: make an iterator that returns elements from the first iterable."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.accumulate
#@ ensures True
#@ assigns \nothing
def accumulate(iterable: int, func: int, *, initial: int) -> int:
    """Mock: make an iterator that returns accumulated results of applying func."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.repeat
#@ requires times >= 0
#@ ensures \result == object
def repeat(object: int, times: int) -> int:
    """Mock: make an iterator that returns object over and over again."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.cycle
# cite:_note: cycle returns an infinite iterator; iterator-sequence semantics (indefinite cycling) cannot be expressed in the current contract surface. Stub models existence of a return value only.
#@ ensures True
def cycle(iterable: int) -> int:
    """Mock: make an iterator that cycles through iterable indefinitely."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.islice
# cite:_note: stop/step constraints live in *args and cannot be individually named; islice object return semantics exceed expressible contract surface
#@ ensures True
def islice(iterable: int, *args: int) -> int:
    """Mock: make an iterator that returns selected elements from the iterable."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.zip_longest
#@ ensures True
# cite:_note: doc semantics exceed expressible contract surface — result is an iterator whose per-element tuple structure and fillvalue substitution cannot be expressed in the Hoare model
def zip_longest(*iterables: int, fillvalue: int) -> int:
    """Mock: make an iterator that aggregates elements from each iterable."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.groupby
#@ ensures True
def groupby(iterable: int, key: int) -> int:
    """Mock: make an iterator that returns consecutive keys and groups from iterable."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.starmap
#@ ensures True
def starmap(func: int, iterable: int) -> int:
    """Mock: make an iterator that computes func using arguments tuples from iterable."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.count
#@ ensures \result == start
def count(start: int, step: int) -> int:
    """Mock: make an iterator that returns evenly spaced values starting with start."""
    return 0
