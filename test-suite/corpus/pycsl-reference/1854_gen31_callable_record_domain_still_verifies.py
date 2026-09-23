r"""Test 1854 — gen #31 SECOND CONTROL for 1852 (expected PASS): a RECORD domain is admissible.

§12.17 admits "record/variant names" alongside the four scalars, and the emission shows the
arrow really is over the record type rather than an erased `int`:

    let function apply (f: py_rec -> int) (r: py_rec) : int

This is the control that matters most, because the natural over-broad repair — "refuse any
bare Name that is not one of the four scalars" — would have taken this with it. The refusal
names the seven collection builtins explicitly instead.
"""
# pycsl-expected: PASS
from typing import Callable

_ = 0  # anchor


class Rec:
    def __init__(self) -> None:
        self.v: int = 0


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def apply(f: Callable[[Rec], int], r: Rec) -> int:
    return 0
