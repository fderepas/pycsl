# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1282 — (#49) ROUTE #99 EXPLOIT ARM: the UB-7.7 memoization gate collected mutated
fields only when the write was spelled `self.<f>`, AND only saw functions emitted before
the end of the enclosing class. Both narrowings had to fall for this file to be refused.

`total` is a `@cached_property` reading `self.a`, and `a` IS mutated — by a free function
taking the object as a parameter, declared after the class. MEASURED AT a32ec69e this file
reported `Verification SUCCESS! All contracts formally proven.` with `c__total'vc` Valid,
and CPython contradicts the proved postcondition:

    before:     total = 0   a = 0
    after bump: total = 0   a = 1     ->  proved `\result == self.a` is FALSE

which is precisely the stale cache (UB-7.7) that route #94's gate exists to reject. Make
the identical mutation a METHOD (`self.a = self.a + 1`) and the gate refused all along —
only the RECEIVER differed. Staleness is a property of THE FIELD, not of who writes it.

>>> A CHECK KEYED ON THE SYNTACTIC SHAPE OF A WRITE TARGET ENUMERATES THE SHAPES ITS
>>> AUTHOR HAPPENED TO PICTURE.

Must FAIL.
"""
_ = 0  # anchor
from functools import cached_property


#@ class invariant self.a >= 0
class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures \result == self.a
    #@ assigns \nothing
    @cached_property
    def total(self) -> int:
        return self.a


#@ requires c.a >= 0
#@ assigns c.a
#@ ensures c.a == \old(c.a) + 1
def bump(c: C) -> None:
    c.a = c.a + 1
