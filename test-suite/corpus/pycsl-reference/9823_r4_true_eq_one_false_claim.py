r"""Test 9823 — dict-value-model-r4 law `True == 1` (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9822's answer).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": True}
    if d.get("a") == 1:
        return 1
    return 0
