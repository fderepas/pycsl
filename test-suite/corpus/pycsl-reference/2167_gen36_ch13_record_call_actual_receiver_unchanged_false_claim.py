r"""Test 2167 — ch13 seam S-b' (expected FAIL): `r.absorb(mk(k))` WRITES `r.n` (its
`assigns self.n`). CPython: `via_fn(5)` returns `1 + 5 == 6`, so `\result == 1` is false.
The abstract op carries the receiver `writes { self.n }`, so the stale value is not provable.
Control: 2166.
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
def via_fn(k: int) -> int:
    r = R(1, 2)
    r.absorb(mk(k))
    return r.n
