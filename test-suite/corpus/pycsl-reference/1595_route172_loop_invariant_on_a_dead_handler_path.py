r"""Test 1595 - ROUTE #172 carrier (gen #29): an `ensures True` function whose `loop invariant r == 0` holds only if the IndexError handler is dead (the read is on a placeholder `[]`) PROVED (CPython r == 9). Loop invariants and variants now count as claims for the handler widening.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ ensures True
def f() -> int:
    xs: List[int] = []
    r = 0
    try:
        r = xs[0]
    except IndexError:
        r = 9
    i = 0
    #@ loop invariant r == 0
    #@ loop variant 3 - i
    while i < 3:
        i = i + 1
    return r
