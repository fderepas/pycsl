r"""Test 8984 -- route #565 witness (expected FAIL): a walrus `(t := x)` rebinding a None-initialised local; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    if (t := x) > 0:
        pass
    if t is None:
        return 0
    return 1
