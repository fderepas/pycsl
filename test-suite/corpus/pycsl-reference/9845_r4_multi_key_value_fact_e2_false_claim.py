r"""Test 9845 — dict-value-model-r4 route (e2) (expected FAIL): the false twin of 9844 (`m.get("c")` is 3, not the value of key "a").
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {"a": 1, "b": 2, "c": 3}}
    m = d.get("m") or {}
    x = m.get("c")
    if x == 3:
        return 3
    return 0
