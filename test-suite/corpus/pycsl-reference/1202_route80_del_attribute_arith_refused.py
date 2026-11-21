"""Test 1202 — ROUTE #80, second carrier: ARITHMETIC on the stale attribute.

The direct read (1201) shows the erased `del c.x` leaves the model holding the instance
value 10 where Python falls back to the class attribute 5. This carrier reads the same
stale value THROUGH AN OPERATOR, and it is the sharper of the two because BOTH directions
land on the same file:

    c = C(); del c.x; return c.x - 5
    #@ ensures \\result == 5      <-- FALSE OF THE PROGRAM (Python returns 0)   PROVED
    #@ ensures \\result == 0      <-- TRUE OF THE PROGRAM                       refused

So the defect is not an artefact of a literal-equality clause being folded away: the stale
field flows into ordinary integer arithmetic and the solver reasons from it.

Refused at the same site as 1201. This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class C:
    x: int = 5

    #@ assigns self.x
    def __init__(self) -> None:
        self.x = 10


#@ requires True
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    c = C()
    del c.x
    return c.x - 5
