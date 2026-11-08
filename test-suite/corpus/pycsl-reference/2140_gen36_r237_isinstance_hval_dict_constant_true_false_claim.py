r"""Test 2140 — route #237 (expected FAIL): `isinstance(x, dict)` on an hval local
(`x = d.get("k", {})`, `d: Dict[str, PyVal]`). At base the pyval arm of `_handle_isinstance`
answered the CONSTANT `true`, so `\result == 1` PROVED (CPython `f({"k": "s"})` = 0). The test
is now the hval constructor discriminant (HMap/HNode true, HStr/HArr false, erased HInt
opaque): undecided for an arbitrary `d`. Controls: 2150, 2151, 2156; tuple form: 2153.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("k", {})
    if isinstance(x, dict):
        return 1
    return 0
