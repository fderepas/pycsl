r"""Test 9829 — dict-value-model-r4 law `None != 0` (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9828's answer).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": None}
    if d.get("a") != 0:
        return 1
    return 0
