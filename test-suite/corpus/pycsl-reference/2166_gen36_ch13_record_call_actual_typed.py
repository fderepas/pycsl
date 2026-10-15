r"""Test 2166 — ch13 seam S-b' (expected PASS): a method call on a record local whose ACTUAL is
a record-valued CALL — `r.absorb(mk(k))` (a same-file function declared `-> R`) and
`r.absorb(R(k, 0))` (a constructor). The abstract method op default-typed its formal `int`, so
both calls were L3-tc errors at base (`r` where `int` is expected). The formal now takes the
record type. Claims here do not depend on the havocked receiver field. Twins: 2167, 2168, 2169.
"""
# pycsl-expected: PASS
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class R:
    n: int
    m: int

    #@ ensures self.n == \old(self.n) + other.n
    #@ assigns self.n
    def absorb(self, other: "R") -> None:
        self.n = self.n + other.n


#@ ensures \result.n == k
#@ assigns \nothing
def mk(k: int) -> R:
    return R(k, 0)


#@ ensures \result == k + 1
#@ assigns \nothing
def via_fn(k: int) -> int:
    r = R(1, 2)
    r.absorb(mk(k))
    return k + 1


#@ ensures \result == k + 2
#@ assigns \nothing
def via_ctor(k: int) -> int:
    r = R(1, 2)
    r.absorb(R(k, 0))
    return k + 2
