"""0444 — behavioral subtyping (Layer D), POSITIVE case.

`Sub.f` overrides `Base.f`, WEAKENING the precondition (`x >= -5` vs `x >= 0`)
and STRENGTHENING the postcondition (`\\result >= x + 1` vs `\\result >= x`).
This is a valid Liskov refinement, so under `--check-behavioral-subtyping` the
goal `(pre_base -> pre_sub) /\\ (post_sub -> post_base)` is provable and the
file verifies.
"""


#@ class invariant self.v >= 0
class Base:
    def __init__(self):
        self.v: int = 0

    #@ requires x >= 0
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x + self.v


class Sub(Base):
    #@ requires x >= -5
    #@ ensures \result >= x + 1
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x + self.v + 1
