"""Test 1211 — ROUTE #83's BOUNDING CONTROL: a STRAIGHT-LINE `__init__` is untouched.

The repair must fire ONLY for a field stored inside control flow. A constructor whose
stores are all top-level is captured exactly as before and stays FAITHFUL IN BOTH
DIRECTIONS — this file proves the TRUE claim.

Without this control the repair could be silently over-broad: emitting an unconstrained
value for every field would close #83 while destroying the parametrized-construction
capability that routes #76 and #82 depend on. That is the `@dataclass` role in #76 and the
positional-parameter role in #82 — a control that BOUNDS the guard rather than merely
witnessing the defect.

The byte-diff agrees: 976/976 pycsl-ref and 2203/2203 python-ref, 0 MOVED / 0 GONE /
0 APPEARED, so no existing emission moved at all.
"""


class C:
    v: int
    w: int

    #@ assigns self.v, self.w
    def __init__(self, n: int) -> None:
        self.v = n + 1
        self.w: int = 5


#@ requires True
#@ ensures \result == 13
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.v + c.w
