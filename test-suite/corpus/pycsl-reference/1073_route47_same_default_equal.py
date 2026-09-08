"""Test 1073 — ROUTE #47 control: two `{}` defaults are EQUAL, and must stay provable.

TRUE OF THE PROGRAM: `{} == {}` is True in Python, so `f()` returns 7.

This is the driver that pins route #47's GRANULARITY, which is a semantic decision and not
a convention — route #41 needed PER-NAME opaques, route #44 needed a SHARED one, and this
route needs one per DEFAULT EXPRESSION. Two syntactically identical defaults denote equal
values, so they must share a constant and stay provably equal; two different ones
(`{}` versus `[]`, `{1: 2}` versus `{3: 4}`) are unequal in Python and must become
undecidable rather than decided. Hashing the default's own IR gives exactly that partition,
and this driver fails if a future change makes the opaque per-SITE instead.
"""
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures True
    def __init__(self) -> None:
        self.x = 1


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C()
    a = getattr(c, "missing", {})
    b = getattr(c, "other", {})
    if a == b:
        return 7
    return 0
