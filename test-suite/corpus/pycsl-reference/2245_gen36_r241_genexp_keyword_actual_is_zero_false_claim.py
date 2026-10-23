r"""Test 2245 — route #241 (expected FAIL): the KEYWORD-actual form of 2242, `g(x=<genexp>)`, also
emitted `g 0` and PROVED `\result == 1` at 1e4b380e while CPython `m()` = 0. Now `g (any int)`;
the postcondition is unproved.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures x == 0 ==> \result == 1
#@ assigns \nothing
def g(x: Any) -> int:
    if x == 0:
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    return g(x=(v for v in [1]))
