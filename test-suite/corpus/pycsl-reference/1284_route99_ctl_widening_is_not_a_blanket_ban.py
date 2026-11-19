# pycsl-flags: --memory-model hoare
# pycsl-expected: PASS
"""1284 — (#49) ROUTE #99 CAPABILITY CONTROL. This one MUST PROVE.

Route #99's repair widens the mutated-field collection to every receiver and moves it to
module scope — strictly more refusals. The danger in that direction is the mistake route
#94 explicitly warned about in its own docstring: "a blanket field-read ban would delete
that real capability (the corpus-1057 mistake)."

Here `total` memoizes a CONSTRUCT-ONLY field `k`, while a foreign-receiver mutator writes a
DIFFERENT field `a`. The widened collection sees `a` mutated and must NOT refuse a reader
of `k`: the gate keys on WHICH field is read, and a `@cached_property` over a field nobody
writes after construction is genuinely referentially transparent — CPython agrees with the
proof. If this file ever starts FAILING, the repair has become the blanket ban.

Companion to 1258, which holds the same capability for the pre-existing `self`-receiver
shape.
"""
_ = 0  # anchor
from functools import cached_property


#@ class invariant self.k >= 0
#@ class invariant self.a >= 0
class C:
    def __init__(self) -> None:
        self.k: int = 7
        self.a: int = 0

    #@ ensures \result == self.k
    #@ assigns \nothing
    @cached_property
    def total(self) -> int:
        return self.k


#@ requires c.a >= 0
#@ assigns c.a
#@ ensures c.a == \old(c.a) + 1
def bump(c: C) -> None:
    c.a = c.a + 1
