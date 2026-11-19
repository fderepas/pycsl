r"""Test 8980 -- route #565 witness (expected FAIL: PROVED at base b432460d6 in hoare / typed / store): `t = None; if x > 0: t, u = 1, 2; if t is None: return 0` folded the test to `pycsl_none = pycsl_none`; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    u = None
    if x > 0:
        t, u = 1, 2
    if t is None:
        return 0
    return 1
