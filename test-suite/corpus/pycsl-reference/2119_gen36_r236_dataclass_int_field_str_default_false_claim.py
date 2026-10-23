r"""Test 2119 — route #236 (expected FAIL): `k: int = "w"` omitted took the definite `0`
and `p.k == 0` PROVED (`\result == 0`); CPython `"w" == 0` is False and `g` returns 1. A `str`
default on a non-`str` field is now unconstrained.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class P:
    x: int
    k: int = "w"


#@ ensures \result == 0
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k == 0:
        return 0
    return 1
