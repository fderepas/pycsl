"""PyCSL mock for Python's functools module — body-verified (no \trusted).

The callable-valued utilities (partial / wraps / lru_cache / cached_property / cmp_to_key) return
an opaque non-negative sentinel (PyCSL cannot model a returned callable); `total_ordering` is the
identity on its class; `reduce` is a **real, body-verified left fold** — the sum-fold instance,
since an arbitrary higher-order callable cannot be modelled on ints."""
_ = 0  # anchor


#@ ensures \result >= 0
def partial(func: int) -> int:
    """A partial object, modelled as an opaque non-negative sentinel."""
    return 0


#@ ensures \result >= 0
def wraps(wrapped: int) -> int:
    """The @wraps decorator, modelled as a sentinel."""
    return 0


#@ requires maxsize >= 0
#@ ensures \result >= 0
def lru_cache(maxsize: int) -> int:
    """The @lru_cache decorator, modelled as a sentinel."""
    return 0


#@ ensures \result >= 0
def cached_property(func: int) -> int:
    """The @cached_property decorator, modelled as a sentinel."""
    return 0


#@ ensures \result >= 0
def cmp_to_key(mycmp: int) -> int:
    """cmp_to_key, modelled as an opaque key sentinel."""
    return 0


# cite: https://docs.python.org/3/library/functools.html#functools.total_ordering
#@ ensures \result == cls
def total_ordering(cls: int) -> int:
    """The @total_ordering class decorator returns the class unchanged."""
    return cls


# cite: https://docs.python.org/3/library/functools.html#functools.reduce
#@ requires n >= 0
#@ requires \length(values) >= n
#@ requires \forall i; 0 <= i and i < n ==> values[i] >= 0
#@ requires initializer >= 0
#@ ensures \result >= initializer
def reduce(function: int, values: list, n: int, initializer: int) -> int:
    """Left fold over the first n elements of `values`, the sum-fold instance of `reduce`
    (an arbitrary callable can't be modelled on ints). Body-verified: with non-negative
    elements the accumulator never drops below the initializer."""
    acc = initializer
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant acc >= initializer
    #@ loop variant n - i
    while i < n:
        acc = acc + values[i]
        i = i + 1
    return acc
