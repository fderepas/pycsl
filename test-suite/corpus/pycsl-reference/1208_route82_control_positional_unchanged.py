"""Test 1208 — ROUTE #82's CONTROL, locked as a corpus test: an ORDINARY POSITIONAL parameter
was always faithful and must stay so.

The control is what made #82 precise rather than alarming. It is the SAME class, the SAME field,
the SAME constructor argument value and the SAME clause as the exploit; only the parameter's
KIND differs. It was FAITHFUL IN BOTH DIRECTIONS before the repair (the false claim refused, the
true claim proved) and it must remain so after it — a repair that changed the positional path
would be touching the one shape that was never broken.

This file proves the TRUE claim (7). Its false twin is 1207's shape one parameter-kind over.
"""


class P:
    v: int

    #@ assigns self.v
    def __init__(self, v: int = 0) -> None:
        self.v = v


#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    p = P(7)
    return p.v
