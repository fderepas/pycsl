"""Test 1110 — ROUTE #56 control (b): the `str` carrier, which FAILS CLOSED — and
fails closed for the WRONG REASON, which is why the route hid for two windows.

The same shape as 1108 at `Optional[str]`. It does not prove, and it never did:
the sentinel for a `str` carrier is `""`, which is ill-typed against the `int`
comparison the emitter builds, so the emission dies with "This expression has type
string, but is expected to have type int".

THAT IS A TYPE ACCIDENT, NOT A GUARD. Routes #50 and #51 probed the `is None`
residue class exhaustively at `str` and found this class safe. It was safe at
`str` and open at `int`. The lesson is recorded in the 30th plane
(`bin/check-type-keyed-value-sentinels.py`): a SAFE-TYPED verdict must name the
carrier it was measured at, because a type-keyed sentinel is only ever safe at the
carriers whose zero does not type-check against the comparand.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Optional


#@ requires c <= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    x: Optional[str] = None
    if c > 0:
        x = "a"
    if x == "":
        return 0
    return 9
