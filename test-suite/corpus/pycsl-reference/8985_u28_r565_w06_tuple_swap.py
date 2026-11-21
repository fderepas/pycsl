r"""Test 8985 -- route #565 witness (expected FAIL): a SWAP `t, u = u, t` rebinding a None-initialised local; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = x
    t, u = u, t
    if t is None:
        return 0
    return 1
