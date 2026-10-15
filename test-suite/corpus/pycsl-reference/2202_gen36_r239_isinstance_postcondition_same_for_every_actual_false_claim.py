r"""Test 2202 — route #239 (expected FAIL): the same parameter NAME across two calls. `g`'s
postcondition `\result == 1 <==> isinstance(x, int)` named the constant `typeof_op 120`, not
the actual, so `g(y)` and `g(z)` were forced to return the same value and `\result == 1`
PROVED at f926a808 while CPython `m(1, "s")` = 0. Control (same actual twice): 2212.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0 or \result == 1
#@ ensures \result == 1 <==> isinstance(x, int)
#@ assigns \nothing
def g(x: Any) -> int:
    if isinstance(x, int):
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m(y: Any, z: Any) -> int:
    a = g(y)
    b = g(z)
    if a == b:
        return 1
    return 0
