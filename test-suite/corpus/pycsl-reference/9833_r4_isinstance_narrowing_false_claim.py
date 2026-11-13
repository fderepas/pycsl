r"""Test 9833 — dict-value-model-r4 law `isinstance narrowing` (expected FAIL): the FALSE claim is NOT proved (CPython runs the honest twin 9832's answer).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Tuple

PyVal = Any


#@ ensures \result == "?"
#@ assigns \nothing
def f(c: int) -> str:
    d: Dict[str, PyVal] = {"a": "x"}
    g = d.get("a")
    if isinstance(g, str):
        return g
    return "?"
