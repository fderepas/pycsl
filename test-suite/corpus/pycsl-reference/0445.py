"""0445 — behavioral subtyping (Layer D), NEGATIVE case.

`Sub.f` overrides `Base.f` but STRENGTHENS the precondition (`x >= 5` vs the
base's `x >= 0`) — a Liskov violation: a caller relying on `Base.f` (which
accepts any `x >= 0`) would break when handed a `Sub`. The override's own body
still verifies, but the refinement goal `(x >= 0 -> x >= 5)` is FALSE, so
verification MUST fail (exit 1): the check rejects bad overrides. Since route
#277 the check is ON BY DEFAULT (it needed `--check-behavioral-subtyping`, and
without it the file "passed": the undeclared CLASS-EXACT assumption).
"""
# pycsl-expected: FAIL

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
