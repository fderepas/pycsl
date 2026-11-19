r"""Test 8996 -- route #565 CONTROL (expected PASS): two None-only locals still compare equal (`None` is one object)
"""
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = None
    if t == u:
        return 0
    return 1
