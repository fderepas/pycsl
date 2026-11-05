r"""Test 8991 -- route #565 witness (expected FAIL): an `Optional[int]` carrier bound `None` on the LAST-EMITTED branch of a join: the AMBIG mark was dropped for the carrier and `None#empty` re-recorded, so `if t:` was decided `false`; CPython f(1) == 1
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Optional


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    t: Optional[int] = None
    if x > 0:
        t = 5
    else:
        t = None
    if t:
        return 1
    return 0
