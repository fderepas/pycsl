r"""Test 9001 -- lvF cap-trusted-val-unit-return (expected FAIL): false twin of 9000. The `-> Any`
`\trusted` stub's `val` now returns an `int`, but an UNCONSTRAINED one: its contract says nothing about
the result, so a claim on the value (`\result == 0`) must not prove. CPython: `lookup` returns None.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Any


#@ \trusted reviewer: lvF
#@ assigns \nothing
def lookup(k: int) -> Any:
    pass


#@ ensures \result == 0
#@ assigns \nothing
def first(k: int) -> Any:
    a = lookup(k)
    return a
