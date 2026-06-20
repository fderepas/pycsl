# Formal tests for pycsl_lib/bsect — bisect module
from pycsl_lib.bsect import bisect_left, bisect_right


#@ requires 0 <= lo
#@ requires lo <= hi
#@ requires hi <= \length(a)
#@ ensures lo <= \result
#@ ensures \result <= hi
def test_bisect_left_bounds(a: list, x: int, lo: int, hi: int) -> int:
    """bisect_left result is always in [lo, hi]."""
    return bisect_left(a, x, lo, hi)


#@ requires 0 <= lo
#@ requires lo <= hi
#@ requires hi <= \length(a)
#@ ensures lo <= \result
#@ ensures \result <= hi
def test_bisect_right_bounds(a: list, x: int, lo: int, hi: int) -> int:
    """bisect_right result is always in [lo, hi]."""
    return bisect_right(a, x, lo, hi)
