r"""Test 9002 -- lvF cap-trusted-val-unit-return (expected FAIL): false twin of 9000. The promoted
`val` is a PROGRAM `val` (not a `val function`): two calls with the same argument are two fresh
values, so equality of two results must not prove (no determinism law is introduced; a `\trusted`
stub may read hidden state).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Any


#@ \trusted reviewer: lvF
#@ assigns \nothing
def lookup(k: int) -> Any:
    pass


#@ ensures \result == 1
#@ assigns \nothing
def same(k: int) -> int:
    a = lookup(k)
    b = lookup(k)
    if a == b:
        return 1
    return 0
