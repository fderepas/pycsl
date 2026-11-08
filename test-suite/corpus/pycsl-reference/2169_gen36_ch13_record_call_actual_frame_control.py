r"""Test 2169 — ch13 seam S-b' (expected PASS, frame control): `r.absorb(mk(k))` assigns ONLY
`self.n`, so `r.m` is unchanged. CPython: `via_fn(k)` returns 2. The abstract op's frame is
exactly the method's `assigns` (`writes { self.n }`), so the untouched field stays provable.
Control for 2166-2168.
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


#@ ensures \result == 2
#@ assigns \nothing
def via_fn(k: int) -> int:
    r = R(1, 2)
    r.absorb(mk(k))
    return r.m
