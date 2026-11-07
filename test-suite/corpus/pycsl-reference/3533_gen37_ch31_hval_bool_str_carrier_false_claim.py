r"""Test 3533 — gen #37 ch31 (expected FAIL): 3532 with `\result == 2`: false in CPython.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"t": "x"}
    if bool(d.get("t")):
        return 1
    return 2
