r"""Test 8997 -- route #565 CONTROL (expected PASS): a tuple unpack of OTHER names leaves a None-only local's fold decided
"""
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    a, b = x, 2
    if t is None:
        return 0
    return 1
