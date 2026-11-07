r"""Test 8982 -- route #565 witness (expected FAIL): the `is not None` spelling of 8980 folded to `not (pycsl_none = pycsl_none)`; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = None
    if x > 0:
        t, u = 1, 2
    if t is not None:
        return 1
    return 0
