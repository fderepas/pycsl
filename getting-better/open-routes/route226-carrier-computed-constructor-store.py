"""ROUTE #226 CARRIER (third shape) — the constructor COMPUTES the field's value.

This file PROVES A FALSE CONTRACT TODAY, which is why it lives here and not in the corpus:
`pycsl-expected: FAIL` would be an XPASS (a red suite) and `PASS` would write "this false
proof is expected" into the reference set. `bin/check-open-route-carriers.py` runs it and
asserts the verdict this route's record states.

THE TWO CARRIERS BEFORE THIS ONE ARE CLOSED. Increment 1 states the obligation for a
paramless constructor storing int literals; increment 2 states it for a field bound to an
`__init__` PARAMETER (and for a `@dataclass`, whose synthesized `__init__` is the same
shape), quantifying over the parameter and carrying `__init__`'s own `#@ requires` as
premises. This shape is what is left.

`self.n = three()` is a COMPUTED store: Module 5 marks the field in `init_unknown_fields`,
so the model does not claim to know its value, and the emitter emits no goal. The invariant
is still assumed by every method, and `read(C())` is 3 in CPython while the published
contract says `>= 5`.

WHY A PREMISE-FREE GOAL IS NOT THE ANSWER (the (u4) test, applied in advance): `forall n.
n >= 5` would refuse a class whose constructor computes a value that DOES satisfy the
invariant, which is an ordinary good program. The obligation needs the CALLEE'S
POSTCONDITION — `three()` ensures `\\result == 3` — and that is increment 3.

EXPECTED TODAY: SUCCESS. CPython: `read(C())` is 3, and `3 >= 5` is False.

WHEN THIS STOPS PROVING, the route is probably closed and
`route226-a-class-invariant-the-constructor-never-establishes.md` must be updated in the
SAME commit — that is the whole point of the carrier gate.
"""
_ = 0  # anchor


#@ ensures \result == 3
#@ assigns \nothing
def three() -> int:
    return 3


#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n = three()

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n


#@ ensures \result >= 5
#@ assigns \nothing
def read(c: C) -> int:
    return c.get()
