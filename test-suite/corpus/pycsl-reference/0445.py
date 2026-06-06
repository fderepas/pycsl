"""0445 — behavioral subtyping (Layer D), NEGATIVE case.

`Sub.f` overrides `Base.f` but STRENGTHENS the precondition (`x >= 5` vs the
base's `x >= 0`) — a Liskov violation: a caller relying on `Base.f` (which
accepts any `x >= 0`) would break when handed a `Sub`. The override's own body
still verifies, so the file passes WITHOUT the flag; but under
`--check-behavioral-subtyping` the refinement goal `(x >= 0 -> x >= 5)` is
FALSE, so verification MUST fail (exit 1). This is the test that the check
actually rejects bad overrides, not just rubber-stamps good ones.
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
    #@ requires x >= 5
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x + self.v
