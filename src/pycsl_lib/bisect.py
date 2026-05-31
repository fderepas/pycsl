"""PyCSL mock for Python's bisect module — Array bisection algorithms for binary searching."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def bisect_left(a: int, x: int, lo: int, hi: int, key: int) -> int:
    """Mock: Locate the insertion point for *x* in *a* to maintain sorted order. The parameters *lo* and *hi* may be used to specify ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bisect_right(a: int, x: int, lo: int, hi: int, key: int) -> int:
    """Mock: Similar to :py:func:`~bisect.bisect_left`, but returns an insertion point which comes after (to the right of) any existi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def insort_left(a: int, x: int, lo: int, hi: int, key: int) -> int:
    """Mock: Insert *x* in *a* in sorted order. This function first runs :py:func:`~bisect.bisect_left` to locate an insertion point...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def insort_right(a: int, x: int, lo: int, hi: int, key: int) -> int:
    """Mock: Similar to :py:func:`~bisect.insort_left`, but inserting *x* in *a* after any existing entries of *x*. This function fir..."""
    return 0
