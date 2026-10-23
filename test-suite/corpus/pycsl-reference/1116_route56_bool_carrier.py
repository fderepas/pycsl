"""Test 1116 — ROUTE #56 negative witness (d): the `bool` CARRIER, which was live too.

FALSE OF THE PROGRAM: `None == False` is False in Python, so with `c <= 0` the `if`
is not taken and `f` returns 9, not 0.

Module 5 maps `bool` onto `int` (`Module5_IREmitter.py`), so an `Optional[bool]`
local's Some-arm carrier is an `int` and the value-read projection answered the very
same type-keyed sentinel `0` that witness 1108 exercises at `Optional[int]`. `False`
lowers to `0`, the `None` arm answered `0`, and the two became the same term.

MEASURED AS A BEFORE/AFTER PAIR rather than asserted (relaunch #51): at the parent
commit this file PROVES `\\result == 0`; with route #56's repair — the non-Some arm
answering route #44's existing `pycsl_none` opaque — it fails closed.

It is kept because it shows route #56's reach was WIDER than the three witnesses
first written for it: the class is "every carrier whose Why3 type matches the
comparand's", and `bool` is in it precisely because it is not a distinct Why3 type
here. The `str` carrier (1110) escapes only by a type accident.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Optional


#@ requires c <= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(c: int) -> int:
    x: Optional[bool] = None
    if c > 0:
        x = True
    if x == False:
        return 0
    return 9
