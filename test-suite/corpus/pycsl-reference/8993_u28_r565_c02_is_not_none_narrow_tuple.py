r"""Test 8993 -- route #565 CONTROL (expected PASS): `is not None` narrowing of a None-initialised local rebound by tuple unpacking keeps proving
"""
from __future__ import annotations


#@ ensures \result >= 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = None
    if x > 0:
        t, u = 1, 2
    if t is not None:
        return t
    return 0
