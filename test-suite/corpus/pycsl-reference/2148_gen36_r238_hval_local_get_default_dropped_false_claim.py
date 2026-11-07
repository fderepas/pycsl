r"""Test 2148 — route #238 (expected FAIL): `.get(k, 5)` on an hval LOCAL answered the missing
key with the empty MAP whatever the default was, and the outer `d.get("k", {})` answered its
missing key with `HInt 0` — so the read compared `== 0` and `\result == 1` PROVED (CPython
`f({})`: `{}.get("j", 5)` is 5, `5 == 0` is False, result 0). Both defaults are now the
literal tagged by `_pyval_wrap` (`HMap PNil`, `HInt 5`).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ requires not ("k" in d)
#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("k", {})
    y = x.get("j", 5)
    if y == 0:
        return 1
    return 0
