r"""Test 9856 — dict-value-model-r4 law `True == 1` (store) (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9855's answer).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": True}
    if d.get("a") == 1:
        return 1
    return 0
