r"""Test 8995 -- route #565 CONTROL (expected PASS): a tuple-unpack rebinding of a None-initialised local; the other target is read exactly
"""
from __future__ import annotations


#@ ensures \result == 2
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    t, u = x, 2
    return u
