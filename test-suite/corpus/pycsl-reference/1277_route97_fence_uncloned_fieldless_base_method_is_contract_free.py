# pycsl-expected: FAIL
"""1277 — (#49) ROUTE #97's NAMED FENCE, kept as a standing witness.

Route #97's repair splits `apply_inheritance`'s loop into two jobs and makes only the
RECORDING half unconditional. The CLONING half stays gated on the base carrying a record,
and this file is the measurement that says why that is safe: an inherited, NOT-overridden
method of a fieldless base is FAIL-CLOSED TODAY. It lowers to a CONTRACT-FREE abstract
val — measured verbatim at a32ec69e and unchanged by the repair:

    val s_f_1 (x0: int) : int

so NOTHING about its result is derivable in either direction. The TRUE fact asserted here
(`\result == 4`, and CPython agrees) does NOT prove, and the FALSE twin (`\result == 99`)
does not prove either. The fielded twin of this file, where cloning DOES happen, proves
the true fact — so the channel is alive and this is a real fence, not a dead probe.

>>> WHY THIS IS A NEGATIVE WITNESS AND NOT A TODO: the obvious "completeness fix" here is
>>> to hand the un-cloned call the BASE's contract. That would ASSUME a postcondition that
>>> NOTHING discharges for the subclass — the campaign's "a completeness fix that supplies
>>> a WITNESS value is a soundness route waiting to happen", which `_field_default` walked
>>> into five times. If this file ever XPASSes, that fix (or an equivalent) has landed and
>>> must be re-audited before it is believed.
"""


class Base:
    #@ requires x >= 0
    #@ ensures \result == x + 1
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x + 1


class Sub(Base):
    pass


#@ ensures \result == 4
#@ assigns \nothing
def driver() -> int:
    s = Sub()
    return s.f(3)
