r"""Test 8999 -- route #565 CONTROL (expected PASS): a `match` capture rebinding, `is not None` narrowing
"""
from __future__ import annotations


#@ ensures \result >= 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    match x:
        case 0:
            pass
        case t:
            pass
    if t is not None:
        return 1
    return 0
