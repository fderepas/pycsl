r"""Test 2143 — routes #237 + #238 (expected FAIL): `x = d.get("k", {}) or {}` then
`isinstance(x, dict)`. At base BOTH halves forced the answer: the `or {}` recognizer replaced
every non-map value by the empty map, and `isinstance(<hval>, dict)` was the constant `true`
anyway — `\result == 1` PROVED (CPython `f({"k": "s"})` = 0: `"s"` is truthy, kept, not a
dict). Now the truthy string is kept and its `HStr` tag answers False: not proved.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("k", {}) or {}
    if isinstance(x, dict):
        return 1
    return 0
