r"""Test 1812 — WITNESS: a global-object method called in EXPRESSION position whose body
does not end in a `return`.

`x = g.bump(n)` needs the inliner to produce a VALUE, and the inliner builds that value
from the callee's trailing `return`. A body whose last statement is an `if/else` — even
when every arm assigns — has no trailing `return` to take, so the inline is refused rather
than completed with a default.

The shape matters and the negative control is in the file's own history: the SAME method
with `return n` / `return 0` at the end inlines and verifies. It is the absence of the
trailing `return`, not the branching, that is refused.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires n >= 0
    #@ assigns self.v
    def bump(self, n: int) -> int:
        if n > 0:
            self.v = n
        else:
            self.v = 0


g = C()


#@ requires n >= 0
#@ ensures \result >= 0
def use(n: int) -> int:
    x = g.bump(n)
    return x
