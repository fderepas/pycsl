# pycsl-flags: --check-behavioral-subtyping
# pycsl-expected: FAIL
"""1275 — (#49) ROUTE #97, the third cell of the 2x2: the BASE is fieldless but the
SUBCLASS carries a field.

This is the cell that proves the drop was keyed on the BASE's record and not on "neither
class has state": at HEAD it also emitted zero goals and reported SUCCESS, even though
`Sub` itself is a perfectly ordinary record. `records.get(bname)` is a lookup of the
BASE's name, so the subclass's own fields never entered into it.

Must FAIL after the repair: the override strengthens the precondition.
"""


class Base:
    #@ requires x >= 0
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x


#@ class invariant self.w >= 0
class Sub(Base):
    def __init__(self):
        self.w: int = 0

    #@ requires x >= 5
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x + self.w
