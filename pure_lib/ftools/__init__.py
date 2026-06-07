# pure_lib/ftools — pure-Python functools module model
# Named 'ftools' to avoid stdlib name clash.
#
# Contracts derived from library_reference/functools.rst.
# RST: "Higher-order functions and operations on callable objects."
# RST: "reduce() — apply function of two arguments cumulatively."
# RST: "partial() — freeze some arguments of a function."
# RST: "lru_cache() — decorator to cache function results."


#@ requires func >= 0
#@ requires n >= 0
#@ ensures \result >= 0
def reduce_count(func: int, n: int) -> int:
    """RST: 'Apply function of two arguments cumulatively to the items
    of iterable, so as to reduce the iterable to a single value.'
    Model: n items reduced = n-1 applications. Returns result."""
    if n == 0:
        return 0
    return n


#@ requires func >= 0
#@ requires nargs >= 0
#@ ensures \result >= 0
#@ ensures \result == func
def partial(func: int, nargs: int) -> int:
    """RST: 'Return a new partial object which when called will behave
    like func called with the positional arguments args.'
    Model: returns func id (partial is just func with frozen args)."""
    return func


#@ requires func >= 0
#@ ensures \result == func
def cache(func: int) -> int:
    """RST: 'Simple lightweight unbounded function cache.'
    Decorator returns same function (semantically identical)."""
    return func


#@ requires func >= 0
#@ requires maxsize >= 0
#@ ensures \result == func
def lru_cache(func: int, maxsize: int) -> int:
    """RST: 'Decorator to wrap a function with a memoizing callable
    that saves up to the maxsize most recent calls.'
    Returns same function (observationally equivalent)."""
    return func


#@ requires func >= 0
#@ ensures \result == func
def wraps(func: int) -> int:
    """RST: 'This is a convenience function for invoking
    update_wrapper() as a function decorator.'
    Returns the function unchanged."""
    return func


#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures \result >= a
#@ ensures \result >= b
def total_ordering_cmp(a: int, b: int) -> int:
    """Model for @total_ordering comparison result.
    RST: 'Given a class defining __eq__ and one ordering method,
    this decorator supplies the rest.' Returns max (comparison bound)."""
    if a >= b:
        return a
    return b


""  # pycsl
#@ class invariant self._hits >= 0
#@ class invariant self._misses >= 0
class CacheInfo:
    """RST: 'Named tuple showing hits, misses, maxsize, currsize.'"""

    def __init__(self):
        self._hits = 0
        self._misses = 0

    #@ ensures self._hits == \old(self._hits) + 1
    #@ assigns self._hits
    def hit(self) -> None:
        """Record a cache hit."""
        self._hits = self._hits + 1

    #@ ensures self._misses == \old(self._misses) + 1
    #@ assigns self._misses
    def miss(self) -> None:
        """Record a cache miss."""
        self._misses = self._misses + 1

    #@ ensures \result == self._hits
    #@ assigns \nothing
    def get_hits(self) -> int:
        """RST: 'Number of cache hits.'"""
        return self._hits

    #@ ensures \result == self._misses
    #@ assigns \nothing
    def get_misses(self) -> int:
        """RST: 'Number of cache misses.'"""
        return self._misses
