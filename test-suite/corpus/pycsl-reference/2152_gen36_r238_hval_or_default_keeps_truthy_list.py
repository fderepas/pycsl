r"""Test 2152 — route #238 (expected PASS): CONTROL for 2142. `v or []` KEEPS a truthy list:
`d.get("args", []) or []` on `{"args": [1, 2]}` is `[1, 2]`, so `\result == 2` PROVES (at
base the list was replaced by the empty map and the length read 0).
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def g(c: int) -> int:
    d: Dict[str, PyVal] = {"args": [1, 2]}
    a = d.get("args", []) or []
    return len(a)
