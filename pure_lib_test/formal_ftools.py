# Formal tests for pure_lib/ftools — functools module
from pure_lib.ftools import reduce_count, partial, cache, lru_cache, wraps


#@ requires func >= 0
#@ requires n >= 0
#@ ensures \result >= 0
def test_reduce_nonneg(func: int, n: int) -> int:
    """reduce result is non-negative."""
    return reduce_count(func, n)


#@ requires func >= 0
#@ ensures \result == func
def test_partial_preserves_func(func: int) -> int:
    """partial returns the same function id."""
    return partial(func, 5)


#@ requires func >= 0
#@ ensures \result == func
def test_cache_identity(func: int) -> int:
    """cache decorator returns same function."""
    return cache(func)


#@ requires func >= 0
#@ ensures \result == func
def test_lru_cache_identity(func: int) -> int:
    """lru_cache decorator returns same function."""
    return lru_cache(func, 128)


#@ requires func >= 0
#@ ensures \result == func
def test_wraps_identity(func: int) -> int:
    """wraps returns function unchanged."""
    return wraps(func)
