# pycsl-flags: --check-behavioral-subtyping
# pycsl-expected: PASS
"""1274 — (#49) ROUTE #97, THE CAPABILITY ARM. This one MUST PROVE.

The mirror image of 1273: a FIELDLESS base whose subclass WEAKENS the precondition
(`x >= 0` vs the base's `x >= 5`) and keeps the postcondition — a legitimate, conforming
refinement. The repair must make the fieldless-base pair CHECKED, not REJECTED.

THIS WITNESS IS ONLY MEANINGFUL BECAUSE THE GOAL NOW EXISTS. At HEAD it also "passed",
vacuously, with zero refinement goals emitted — a guard whose population is empty looks
exactly like a guard that passed. After the repair the emitted goal is
`sub__f_refines_base : forall self: sub, x: int, result: int.
((x >= 5) -> (x >= 0)) /\ ((result >= x) -> (result >= x))`, and alt-ergo returns Valid.
"""


class Base:
    #@ requires x >= 5
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x


class Sub(Base):
    #@ requires x >= 0
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x
