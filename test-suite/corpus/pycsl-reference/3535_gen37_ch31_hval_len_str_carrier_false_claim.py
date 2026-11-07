r"""Test 3535 — gen #37 ch31 (expected FAIL): 3534 with `\result == 0` (the old `hval_len`
reading of a non-list carrier): false in CPython.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"s": "abc"}
    return len(d.get("s"))
