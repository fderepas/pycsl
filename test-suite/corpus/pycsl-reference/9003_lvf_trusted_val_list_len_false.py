r"""Test 9003 -- lvF cap-trusted-val-unit-return (expected FAIL): false twin of 9000. The
`-> List[int]` `\trusted` stub's `val` returns an unconstrained `array int`: its length is unknown,
so `len(items(k)) == 0` must not prove (CPython would raise on `len(None)`; the model claims nothing).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List


#@ \trusted reviewer: lvF
#@ assigns \nothing
def items(k: int) -> List[int]:
    pass


#@ ensures \result == 0
#@ assigns \nothing
def count(k: int) -> int:
    xs = items(k)
    return len(xs)
