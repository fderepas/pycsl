"""Test 1115 — ROUTE #57 POSITIVE control: the EXPLICIT-default form is CORRECT and
the repair must not cost it.

TRUE OF THE PROGRAM: `{1: 2}.get(5, 7)` really is 7 in Python, so `f` returns 1.

The two-argument `.get` is the one case where the model's answer for a missing key is
the right one, because Python genuinely answers the supplied default. Route #57's
repair changes ONLY the one-argument form, where Python answers `None`. This file
pins that boundary: a repair that fixed the route by making every `.get` opaque would
pass 1112-1114 and fail here, and would have thrown away a correct answer to buy a
sound one.
"""
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 2}
    if d.get(5, 7) == 7:
        return 1
    return 0
