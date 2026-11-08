r"""Test 8994 -- route #565 CONTROL (expected PASS at base and HEAD): a None-only local keeps its decided truthiness `false` (no other binding form)
"""
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    if t:
        return 7
    return 0
