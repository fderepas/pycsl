r"""Test 3534 — gen #37 ch31 (expected PASS): `len(d.get("s"))` on an `HStr "abc"` carrier is the string
length 3 (CPython: 3). At 0f7cb454 it was `iter_length <hval>`: L3-tc.
"""
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"s": "abc"}
    return len(d.get("s"))
