r"""Test 2151 — route #237/#238 (expected PASS): CONTROL. With "k" absent, `d.get("k", {})` IS
the empty dict: the default is now tagged `HMap PNil` (it was the `HInt 0` sentinel), so
`isinstance(x, dict)` decides True and `\result == 1` PROVES.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ requires not ("k" in d)
#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("k", {})
    if isinstance(x, dict):
        return 1
    return 0
