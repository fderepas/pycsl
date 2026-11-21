r"""Test 8989 -- route #565 witness (expected FAIL): a single-element tuple target `t, = (x,)`; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    t, = (x,)
    if t is None:
        return 0
    return 1
