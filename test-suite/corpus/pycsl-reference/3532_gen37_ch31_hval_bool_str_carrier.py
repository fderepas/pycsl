r"""Test 3532 — gen #37 ch31 (expected PASS): `bool({"t": "x"}.get("t"))` is True on the `HStr "x"`
carrier (CPython: 1). At 0f7cb454: `bool_conv` on an hval, L3-tc.
"""
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"t": "x"}
    if bool(d.get("t")):
        return 1
    return 2
