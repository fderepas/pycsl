"""Test 1222 — ROUTE #87: a list field's literal keeps its LENGTH and loses every ELEMENT to a
definite `0`.

`_field_default`'s list arm returned `(Array.make <len> 0)`. Module 5 captures the length via
`_array_init_size`, so the model is RIGHT about the shape and WRONG about the contents — and
`Array.make` makes the wrong contents DECIDABLE rather than unknown, which is what turns an
imprecision into a route. Measured before the repair: this claim PROVED, CPython returns 1.
The TRUE twin (1223) was refused.

**HOW IT WAS FOUND, AND IT CAUGHT A CONTROL WRITTEN EARLIER IN THE SAME SESSION.** Route #85's
control table records "a LIST field is fail-closed". That control ran exactly ONE operation —
`len(c.xs)` — and the LENGTH really is faithful, so the control was TRUE and useless as a
general claim. Probing a SECOND operation on the same carrier took two minutes.

**A CONTROL IS A MEASUREMENT ABOUT THE OPERATION IT RAN, NEVER A THEOREM ABOUT THE TYPE.** That
is route #81's generator, which refuted route #59's "lists alias correctly" on exactly this
axis — #59 had measured an element STORE and the LENGTH-changing mutation was the unmeasured
one. **THIS IS THE MIRROR IMAGE: length right, elements wrong.** Keep the pair together: for a
collection, ALWAYS probe both the shape and the contents, because neither implies the other in
either direction.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[0]
