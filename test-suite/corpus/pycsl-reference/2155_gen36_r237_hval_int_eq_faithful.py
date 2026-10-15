r"""Test 2155 — route #237/#238 (expected PASS): CONTROL for 2145. A KNOWN int value (`HInt 5`)
compared `== 5` is decided True through the `HInt` arm: `\result == 1` PROVES.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": 5}
    if d.get("a") == 5:
        return 1
    return 0
