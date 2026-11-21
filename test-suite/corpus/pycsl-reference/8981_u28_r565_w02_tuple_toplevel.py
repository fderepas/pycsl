r"""Test 8981 -- route #565 witness (expected FAIL): a TOP-LEVEL tuple-unpack rebinding kept the linear None record; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    t, u = x, 2
    if t is None:
        return 0
    return 1
