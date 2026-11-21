r"""Test 8987 -- route #565 witness (expected FAIL): route #44's decided truthiness `false` survived a tuple-unpack rebinding; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    t, u = 5, 2
    if t:
        return 1
    return 0
