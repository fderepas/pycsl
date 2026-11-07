r"""Test 3474 — gen #37 ch30 (expected PASS): an hval actual `holder.get("records", [])` passed to
a `List[Dict[str, PyVal]]` parameter goes through `hval_to_seq` (`HArr HNil` -> the empty seq),
so the callee contract `len(fns) >= 1` rules out `return 1` (CPython: 0). At acde8476: L3-tc.
"""
# pycsl-expected: PASS
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
    holder: Dict[str, PyVal] = {"records": []}
    if has_c(holder.get("records", [])):
        return 1
    return 0
