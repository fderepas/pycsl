r"""Test 2206 — route #239 (expected FAIL): the STATE-keyed form of route #197/#213's UNKNOWN
`getattr` device (`pycsl_getattr_unknown_<site> !_pyobj_state`) separates two reads across a
WRITE but not across a REBINDING of the receiver name — a rebinding writes nothing — so
`\result == 0` PROVED at f926a808 while CPython `f(C(1), C(2))` = -1. Now the device takes
the receiver value too. Control: 2214.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
def f(o: Any, p: Any) -> int:
    x = getattr(o, "a", 0)
    o = p
    y = getattr(o, "a", 0)
    return x - y
