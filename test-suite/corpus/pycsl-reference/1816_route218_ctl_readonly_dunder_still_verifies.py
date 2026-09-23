r"""Test 1816 — ROUTE #218 CONTROL (expected PASS): a READ-ONLY dunder is untouched.

Route #218's repair frames the abstract `val` minted for an explicitly-called dunder with
the self-fields its DROPPED BODY writes. The control that keeps that honest is a dunder
whose body writes NOTHING: it must still be modelled as pure, the `val` must carry no
`writes` clause, and this program must still verify.

Without this file the repair would be indistinguishable from a blanket "every dunder call
clobbers the receiver", which would be a needless loss of provable facts — and exactly the
kind of over-broad fix route #13's census already refused once.
"""
# pycsl-expected: PASS


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    def __enter__(self) -> int:
        return self.v


#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _r: int = c.__enter__()
    after: int = c.v
    return before - after
