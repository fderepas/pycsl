r"""Test 8990 -- route #565 witness (expected FAIL): a NESTED `def t` rebinding a None-initialised local `t` (the lift dropped the binding); now refused as a lifted-name collision; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t = None
    def t() -> int:
        return 1
    if t is None:
        return 0
    return 1
