r"""Test 9821 — dict-value-model-r4 law `absent key vs stored None` (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9820's answer).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": None}
    if d.get("a") is None and d.get("b") is None and "a" in d and "b" not in d:
        return 1
    return 0
