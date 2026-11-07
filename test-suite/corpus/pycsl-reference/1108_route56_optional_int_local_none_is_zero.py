"""Test 1108 — ROUTE #56 negative witness (a): a `None` Optional-union LOCAL read
back as the carrier's ZERO, so `None == 0` was DECIDABLY TRUE.

FALSE OF THE PROGRAM: Python's `None == 0` is False, so with `c <= 0` the `if` is
not taken and `f` returns 9, not 0.

THE STORAGE WAS ALWAYS FAITHFUL AND THE READ WAS NOT. Module 5 synthesizes
`type _union_f_0 = Arm_0_0 int | Arm_0_None` from the ordinary `Optional[int]`
annotation, and `x` really is initialized to the distinct `Arm_0_None`
constructor. What erased it was the VALUE-READ projection
(`expressions._union_read_projection`), whose non-Some arm answered a type-keyed
SENTINEL: `match !x with Arm_0_0 _v -> _v | _ -> 0 end`. For an `int` carrier the
sentinel and the comparand have the same Why3 type, so a `None` local and a
genuine `0` became THE SAME TERM.

This is route #44's defect (`None` was the integer 0) reaching through a door
#44's shared opaque never covered. The fix answers route #44's EXISTING
`val function pycsl_none : int` in the non-Some arm instead of a zero — no new
model, no new axiom — so the comparison is UNDECIDED rather than wrong.

WHY IT SURVIVED ROUTES #50 AND #51, which probed this class exhaustively: they
probed it at `str`, where the same sentinel (`""`) is ILL-TYPED against the
comparand and the emission dies on a Why3 type error. That is an ACCIDENT, not a
guard. `int` is the carrier where the sentinel type-checks, and it was the only
one that decided. 1110 is the `str` control.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Optional


#@ requires c <= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    x: Optional[int] = None
    if c > 0:
        x = 5
    if x == 0:
        return 0
    return 9
