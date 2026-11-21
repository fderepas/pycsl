r"""Test 2154 — route #238 (expected PASS): CONTROL. With "args" absent, `d.get("args", [])`
is the empty list (`HArr HNil`, falsy), so `... or []` is the empty list and `\result == 0`
PROVES.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ requires not ("args" in d)
#@ ensures \result == 0
#@ assigns \nothing
def g(d: Dict[str, PyVal]) -> int:
    a = d.get("args", []) or []
    return len(a)
