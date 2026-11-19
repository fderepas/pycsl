r"""Test 8986 -- route #565 witness (expected FAIL): two None-initialised locals rebound by tuple unpacking still read the shared `pycsl_none`, so `t == u` was decided True; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = None
    t, u = 1, x + 1
    if t == u:
        return 0
    return 1
