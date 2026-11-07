r"""Test 2205 — route #239 (expected FAIL): route #47's `getattr` device is keyed on the call's
IR (`repr(expr)`), i.e. on the receiver's NAME. In a pure function it is a constant, so
`getattr(o, "a"); o = p; getattr(o, "a")` read ONE term and `\result == 0` PROVED at f926a808
while CPython `f(C(1), C(2))` = -1. The device now also takes the lowered receiver:
`pycsl_getattr_missing_<site> !o`. Control (no rebinding): 1727.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(o: Any, p: Any) -> int:
    x = getattr(o, "a")
    o = p
    y = getattr(o, "a")
    return x - y
