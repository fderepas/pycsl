"""1147 — ROUTE #63 NEGATIVE: "no aliasing is possible" is true for lists, false for sets.

`caller2` takes no parameters and returns a concrete int, so there is no "if a caller
aliases" caveat: the aliasing happens INSIDE the proven unit. It proved `\result == 0`
for a function CPython answers 7 on.

A set lowers to a PURE Why3 `map`, which has no region, so the alias barrier that refuses
`f(xs, xs)` on two LIST params ("This application creates an illegal alias") cannot exist
here. Must never prove again.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires 1 not in t
    #@ ensures \result == 0
    #@ assigns \nothing
    def helper(self, s: Set[int], t: Set[int]) -> int:
        s.add(1)
        if 1 in t:
            return 7
        return 0

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def caller2(self) -> int:
        u: Set[int] = set()
        return self.helper(u, u)
