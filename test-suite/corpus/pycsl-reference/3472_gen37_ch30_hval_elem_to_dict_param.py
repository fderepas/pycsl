r"""Test 3472 — gen #37 ch30 (expected PASS): an hval loop element (an HMap) passed to a
`Dict[str, PyVal]` parameter goes through `hval_to_map` (the definitional assoc-list view), so
the callee contract `"answer" in rec` is checked against the REAL element: neither record has
the key, `return 1` is unreachable (CPython: 0). At acde8476: L3-tc (hval vs map).
"""
# pycsl-expected: PASS
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
    holder: Dict[str, PyVal] = {"records": [{"x": "Valid"}, {"y": "Valid"}]}
    for r in holder.get("records", []):
        if is_valid(r):
            return 1
    return 0
