"""PyCSL mock for Python's bisect module — Array bisection algorithms for binary searching."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/bisect.html#bisect.bisect_left
#@ requires lo >= 0
#@ requires hi >= lo
#@ ensures \result >= lo
#@ ensures \result <= hi
def bisect_left(a: int, x: int, lo: int, hi: int, key: int) -> int:
    """Mock: Locate the insertion point for *x* in *a* to maintain sorted order. The parameters *lo* and *hi* may be used to specify ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/bisect.html#bisect.bisect_right
#@ requires lo >= 0
#@ requires lo <= hi
#@ ensures \result >= lo
#@ ensures \result <= hi
def bisect_right(a: int, x: int, lo: int, hi: int, key: int) -> int:
    """Mock: Similar to :py:func:`~bisect.bisect_left`, but returns an insertion point which comes after (to the right of) any existi..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/bisect.html#bisect.insort_left
#@ requires lo >= 0
#@ requires hi >= lo
#@ ensures True
def insort_left(a: int, x: int, lo: int, hi: int, key: int) -> int:
    """Mock: Insert *x* in *a* in sorted order. This function first runs :py:func:`~bisect.bisect_left` to locate an insertion point...."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/bisect.html#bisect.insort_right
#@ requires lo >= 0
#@ requires hi >= lo
#@ ensures True
def insort_right(a: int, x: int, lo: int, hi: int, key: int) -> int:
    """Mock: Similar to :py:func:`~bisect.insort_left`, but inserting *x* in *a* after any existing entries of *x*. This function fir..."""
    return 0
