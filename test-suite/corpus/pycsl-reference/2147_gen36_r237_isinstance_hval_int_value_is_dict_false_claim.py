r"""Test 2147 — route #237 (expected FAIL): a KNOWN int value (`{"a": 5}`) read into an hval
local was still "a dict" under the constant-`true` arm, so `\result == 1` PROVED (CPython
`f(0)` = 0). The erased `HInt` carrier answers `isinstance(.., dict)` opaquely: not proved.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": 5}
    x = d.get("a", {})
    if isinstance(x, dict):
        return 1
    return 0
