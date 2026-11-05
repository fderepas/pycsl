r"""Test 8998 -- route #565 CONTROL (expected PASS): a NaN-only local keeps route #45's exact `t == t` -> False
"""
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = float("nan")
    if t == t:
        return 1
    return 0
