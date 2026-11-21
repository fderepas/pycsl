r"""Test 8992 -- route #565 CONTROL (expected PASS at base and HEAD): a local bound ONLY to None keeps its faithful decided `is None` fold
"""
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    if t is None:
        return 0
    return 1
