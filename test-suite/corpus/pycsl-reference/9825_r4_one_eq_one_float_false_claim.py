r"""Test 9825 — dict-value-model-r4 law `1 == 1.0` (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9824's answer).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": 1}
    if d.get("a") == 1.0:
        return 1
    return 0
