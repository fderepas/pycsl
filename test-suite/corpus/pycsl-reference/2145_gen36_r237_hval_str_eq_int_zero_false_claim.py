r"""Test 2145 — route #237/#238 (expected FAIL): `hval == <int>` lowered to `hint_of v = n`,
and `hint_of` projects EVERY non-int carrier to 0 — so the string `"s"` compared `== 0` was
True and `\result == 1` PROVED (CPython: `"s" == 0` is False, `f(0)` = 0). Only the `HInt`
carrier can now equal an int. Control: 2155.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"a": "s"}
    if d.get("a") == 0:
        return 1
    return 0
