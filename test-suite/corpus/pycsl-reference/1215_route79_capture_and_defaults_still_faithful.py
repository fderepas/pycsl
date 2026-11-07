"""Test 1215 — ROUTE #79's BOUNDING CONTROL: the two FAITHFUL paths must survive the repair,
and this file proves their TRUE claims.

A repair that marked every uncaptured field unconstrained would close #79 and destroy two
capabilities that are correct today:

  1. THE CAPTURE PATH — an RHS over `__init__` PARAMETERS ONLY (`self.x = n + 1`) is
     substitutable into the record literal and is FAITHFUL IN BOTH DIRECTIONS. This is the
     parametrized-construction capability routes #76 and #82 depend on.
  2. THE `field_defaults` PATH — a LITERAL RHS (`self.w = 5`) carries its true value, and
     it does so EVEN IN A PARAMETERLESS `__init__`, which is exactly the constructor shape
     1214 showed was never scanned. Marking literals unknown would have thrown away a value
     the model actually has.

So the repair keys on "the RHS NAMES a free name the record literal cannot substitute" —
NOT on "the RHS was not captured". Those two sets differ by all 376 literal initialisers in
the repository, and the difference is the whole reason this is a soundness fix rather than a
completeness regression.

**WHY A BOUNDING CONTROL AND NOT JUST AN EXPLOIT WITNESS:** an over-broad repair passes every
exploit witness in this family — all of them assert that something must NOT prove, and an
unconstrained value satisfies all of them at once. Only a control that asserts something must
STILL PROVE can fail when the guard grows too wide. Route #83's witness 1211 is the same
instrument for the same emission site.

Both claims below are TRUE of the program and MUST prove.
"""


class C:
    x: int

    #@ assigns self.x
    def __init__(self, n: int) -> None:
        self.x = n + 1


class D:
    w: int

    #@ assigns self.w
    def __init__(self) -> None:
        self.w = 5


#@ requires True
#@ ensures \result == 11
#@ assigns \nothing
def f() -> int:
    c = C(5)
    d = D()
    return c.x + d.w
