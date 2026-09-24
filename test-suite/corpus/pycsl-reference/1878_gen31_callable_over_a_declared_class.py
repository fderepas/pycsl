r"""Test 1878 — gen #31 CONTROL for 1877 (expected PASS): the declared class is admissible.

The same annotation with `Box` really declared, so the refusal is about the NAME being
unresolvable and not a ban on class-typed `Callable` domains — the control discipline
routes #13 and #223 already pay for, and the reason the census before landing mattered: a
refusal that could not tell a declared class from a typo would have taken every
record-typed `Callable` in the tree with it.
"""
# pycsl-expected: PASS
_ = 0  # anchor
from typing import Callable


class Box:
    def __init__(self) -> None:
        self.n: int = 0


#@ requires f(x) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def apply(f: Callable[[Box], int], x: Box) -> int:
    return f(x)
