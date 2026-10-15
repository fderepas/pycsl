r"""Test 2157 — route #238 (expected PASS): CONTROL. With the keys absent, `d.get("k", [])` is
the empty LIST and `d.get("s", "")` the empty STRING: both defaults are now tagged by their
own literal (`HArr HNil` / `HStr ""`; the list default was the `HInt 0` sentinel and the
string default an ill-typed raw literal), so both type tests decide True and `\result == 1`
PROVES.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ requires not ("k" in d) and not ("s" in d)
#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("k", [])
    y = d.get("s", "")
    if isinstance(x, list) and isinstance(y, str):
        return 1
    return 0
