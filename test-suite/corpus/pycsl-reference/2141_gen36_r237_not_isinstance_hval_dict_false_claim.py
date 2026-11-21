r"""Test 2141 — route #237 (expected FAIL): the negated form of 2140. `not isinstance(x, dict)`
was the constant `not true`, so the early `return 0` was dead and `\result == 1` PROVED
(CPython `h({"k": 5})` = 0). Now undecided.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def h(d: Dict[str, PyVal]) -> int:
    x = d.get("k", {})
    if not isinstance(x, dict):
        return 0
    return 1
