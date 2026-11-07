r"""Test 3531 — gen #37 ch31 (expected FAIL): 3530 with `\result == 1`: false in CPython
(`g({})` is 0).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g(d: Dict[str, PyVal]) -> int:
    x = d.get("t")
    if bool(x):
        if not x:
            return 1
    return 0
