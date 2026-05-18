"""PyCSL mock for Python's functools module.

Provides trusted stubs for higher-order functions and function utilities:
partial application, function wrapping and decorators, memoization,
and comparison utilities.
"""
_ = 0  # anchor

# ── Partial application ────────────────────────────────────────────

#@ \trusted
def partial(func: int, *args: int, **kwargs: int) -> int:
    """Mock: return a new partial object which when called behaves like func."""
    return 0

# ── Decorators ─────────────────────────────────────────────────────

#@ \trusted
def wraps(wrapped: int) -> int:
    """Mock: update wrapper function to look like the wrapped function."""
    return 0

#@ \trusted
def lru_cache(maxsize: int) -> int:
    """Mock: least-recently-used cache decorator for function results."""
    return 0

#@ \trusted
def cached_property(func: int) -> int:
    """Mock: decorator to compute a property value once and cache it."""
    return 0

# ── Reduction ──────────────────────────────────────────────────────

#@ \trusted
def reduce(function: int, iterable: int, initializer: int) -> int:
    """Mock: apply function cumulatively to items of iterable from left to right."""
    return 0

# ── Comparison utilities ───────────────────────────────────────────

#@ \trusted
def total_ordering(cls: int) -> int:
    """Mock: class decorator that fills in ordering methods based on rich comparison."""
    return 0

#@ \trusted
def cmp_to_key(mycmp: int) -> int:
    """Mock: convert a cmp= function into a key= function for sorting."""
    return 0
