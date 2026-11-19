r"""Test 2144 — route #237/#238 (expected FAIL): a 1-argument `.get` on a `Dict[str, PyVal]`
with the key ABSENT is Python `None`. At base the missing-key arm was the definite `HInt 0`
and `== 0` projected through `hint_of`, so `\result == 1` PROVED (CPython: `None == 0` is
False, `f({})` = 0). The arm is now route #44's opaque `HInt pycsl_none`: undecided.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ requires not ("k" in d)
#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    x = d.get("k")
    if x == 0:
        return 1
    return 0
