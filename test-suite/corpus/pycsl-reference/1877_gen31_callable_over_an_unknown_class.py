r"""Test 1877 — gen #31 WITNESS (expected FAIL): a `Callable` over an unknown class.

`Callable[[Rekt], int]` for a `Rekt` that does not exist VERIFIED, emitting `f: int -> int`.
`_callable_tag_to_whyml` resolves a bare name against Module 6's record/variant tables and
falls back to `int` for anything else, with the honest note that "Why3 then rejects the
application if the arg type disagrees, which is sound".

Sound it is — and it is the BACKEND covering for a missing FRONT-END rule, the same
accident that keeps the legacy-`Generic[T]` finding from being a route. A typo in a type
the user wrote should not be answered by a type error about something else, and the
COLLECTION half of this same sentence (`Callable[[bytes], int]`) has been a loud
`PYCSL-TY3-CALLABLE-SCOPE` since gen #31 — which is precisely what made the class half look
enforced.

Control: 1878, the same file with the class actually declared.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Callable


#@ requires f(x) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def apply(f: Callable[[Rekt], int], x: Rekt) -> int:
    return f(x)
