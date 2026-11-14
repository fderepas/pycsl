r"""Test 9835 — dict-value-model-r4 law `insertion order, last-wins duplicate (`tuple(d)` = its keys)` (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9834's answer).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"m": {"b": 1, "a": 2, "b": 3}}
    ks = tuple(d.get("m") or {})
    if len(ks) == 2 and ks[0] == "b" and ks[1] == "a":
        return 1
    return 0
