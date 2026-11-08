r"""Test 3475 — gen #37 ch30 (expected FAIL): 3474 with `records = [{"name": "c"}]`:
CPython returns 1, so `\result == 0` must not prove.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any

#@ ensures \result != False ==> len(fns) >= 1
#@ assigns \nothing
def has_c(fns: List[Dict[str, PyVal]]) -> bool:
    for f in fns:
        if f.get("name") == "c":
            return True
    return False

#@ ensures \result == 0
#@ assigns \nothing
def empty_has_none() -> int:
    holder: Dict[str, PyVal] = {"records": [{"name": "c"}]}
    if has_c(holder.get("records", [])):
        return 1
    return 0
