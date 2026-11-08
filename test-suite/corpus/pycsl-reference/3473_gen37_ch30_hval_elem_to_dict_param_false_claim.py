r"""Test 3473 — gen #37 ch30 (expected FAIL): 3472 with the second record
`{"answer": "Valid"}`: CPython returns 1, so `\result == 0` must not prove.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any

#@ ensures \result != False ==> "answer" in rec
#@ assigns \nothing
def is_valid(rec: Dict[str, PyVal]) -> bool:
    a = rec.get("answer")
    return a == "Valid"

#@ ensures \result == 0
#@ assigns \nothing
def none_valid() -> int:
    holder: Dict[str, PyVal] = {"records": [{"x": "Valid"}, {"answer": "Valid"}]}
    for r in holder.get("records", []):
        if is_valid(r):
            return 1
    return 0
