r"""Test 2150 — route #237 (expected PASS): CONTROL for 2140. A KNOWN dict value (`{"z": 1}`,
built as `HMap`) read into an hval local IS a dict: the constructor discriminant decides
`isinstance(x, dict)` True and `\result == 1` PROVES.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[str, PyVal] = {"k": {"z": 1}}
    x = d.get("k", {})
    if isinstance(x, dict):
        return 1
    return 0
