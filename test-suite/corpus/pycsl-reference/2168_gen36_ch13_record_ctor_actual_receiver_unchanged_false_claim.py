r"""Test 2168 — ch13 seam S-b' (expected FAIL): the constructor-actual twin of 2167.
`r.absorb(R(k, 0))` writes `r.n`; CPython `via_ctor(5)` returns 6, so `\result == 1` is
false and must stay unproved. Control: 2166.
"""
# pycsl-expected: FAIL
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


#@ ensures \result == 1
#@ assigns \nothing
def via_ctor(k: int) -> int:
    r = R(1, 2)
    r.absorb(R(k, 0))
    return r.n
