r"""Test 9827 — dict-value-model-r4 law `(1,) != [1]` (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9826's answer).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": (1,), "b": [1]}
    if d.get("a") != d.get("b"):
        return 1
    return 0
