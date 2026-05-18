"""PyCSL mock for Python's itertools module.

Provides trusted stubs for creating iterators for efficient looping:
combinations, permutations, infinite iteration, and iteration utilities.
"""
_ = 0  # anchor

# ── Combinatorics ─────────────────────────────────────────────────

#@ \trusted
def combinations(iterable: int, r: int) -> int:
    """Mock: return successive r-length tuples of elements from the iterable."""
    return 0

#@ \trusted
def permutations(iterable: int, r: int) -> int:
    """Mock: return successive r-length permutations of elements from the iterable."""
    return 0

#@ \trusted
def product(*iterables: int, repeat: int) -> int:
    """Mock: return cartesian product of input iterables."""
    return 0

# ── Iteration ──────────────────────────────────────────────────────

#@ \trusted
def chain(*iterables: int) -> int:
    """Mock: make an iterator that returns elements from the first iterable."""
    return 0

#@ \trusted
def accumulate(iterable: int, func: int, *, initial: int) -> int:
    """Mock: make an iterator that returns accumulated results of applying func."""
    return 0

#@ \trusted
def repeat(object: int, times: int) -> int:
    """Mock: make an iterator that returns object over and over again."""
    return 0

#@ \trusted
def cycle(iterable: int) -> int:
    """Mock: make an iterator that cycles through iterable indefinitely."""
    return 0

#@ \trusted
def islice(iterable: int, *args: int) -> int:
    """Mock: make an iterator that returns selected elements from the iterable."""
    return 0

#@ \trusted
def zip_longest(*iterables: int, fillvalue: int) -> int:
    """Mock: make an iterator that aggregates elements from each iterable."""
    return 0

#@ \trusted
def groupby(iterable: int, key: int) -> int:
    """Mock: make an iterator that returns consecutive keys and groups from iterable."""
    return 0

#@ \trusted
def starmap(func: int, iterable: int) -> int:
    """Mock: make an iterator that computes func using arguments tuples from iterable."""
    return 0

#@ \trusted
def count(start: int, step: int) -> int:
    """Mock: make an iterator that returns evenly spaced values starting with start."""
    return 0
