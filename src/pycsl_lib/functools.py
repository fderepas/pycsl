"""PyCSL mock for Python's functools module.

Provides trusted stubs for higher-order functions and function utilities:
partial application, function wrapping and decorators, memoization,
and comparison utilities.
"""
_ = 0  # anchor

# ── Partial application ────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/functools.html#functools.partial
# cite:_note: doc semantics exceed expressible contract surface — partial returns a new callable; stub models it as int sentinel
#@ ensures True
def partial(func: int, *args: int, **kwargs: int) -> int:
    """Mock: return a new partial object which when called behaves like func."""
    return 0

# ── Decorators ─────────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/functools.html#functools.wraps
# cite:_note: decorator-factory semantics (callable → callable) exceed the int-stub contract surface; no meaningful numeric pre/postcondition is expressible; L3 ceiling per Part 3 §"When to stop at L3"
#@ ensures True
def wraps(wrapped: int) -> int:
    """Mock: update wrapper function to look like the wrapped function."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/functools.html#functools.lru_cache
#@ requires maxsize >= 0
#@ ensures True
def lru_cache(maxsize: int) -> int:
    """Mock: least-recently-used cache decorator for function results."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/functools.html#functools.cached_property
#@ requires True
#@ ensures True
def cached_property(func: int) -> int:
    """Mock: decorator to compute a property value once and cache it."""
    return 0

# ── Reduction ──────────────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/functools.html#functools.reduce
#@ ensures True
def reduce(function: int, iterable: int, initializer: int) -> int:
    """Mock: apply function cumulatively to items of iterable from left to right."""
    return 0

# ── Comparison utilities ───────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/functools.html#functools.total_ordering
#@ ensures \result == cls
def total_ordering(cls: int) -> int:
    """Mock: class decorator that fills in ordering methods based on rich comparison."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/functools.html#functools.cmp_to_key
#@ ensures True
def cmp_to_key(mycmp: int) -> int:
    """Mock: convert a cmp= function into a key= function for sorting."""
    return 0
