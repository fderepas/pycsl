r"""Test 2142 — route #238 (expected FAIL): `d.get("args", []) or []` on a `Dict[str, PyVal]`.
At base `_recognize_pyval_or_default` emitted `match v with HMap _ -> v | _ -> HMap PNil`: a
truthy list was REPLACED by the empty map and `len` read 0, so `\result == 0` PROVED (CPython
`g({"args": [1, 2]})` = 2). Now `if hval_truthy v then v else HArr HNil`. Controls: 2152, 2154.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def g(d: Dict[str, PyVal]) -> int:
    a = d.get("args", []) or []
    return len(a)
