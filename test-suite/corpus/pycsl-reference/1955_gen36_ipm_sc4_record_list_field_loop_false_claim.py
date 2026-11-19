r"""Test 1955 — gen #36 (expected FAIL): W-IPM S-C4 NON-VACUITY twin of 1954 — same loop,
but the precondition only bounds each element's `n` by -1, so the running sum can go
negative (CPython: one item with n = -1 returns -1). The faithful element read must NOT
prove `\result >= 0`. Original 1954 summary: `for it in self.items` over a
`List[<record>]` self field emitted as the faithful `array item` (S-C3) iterates a snapshot
`let _rl = self.items` with bound `Array.length _rl`, binds `it` to the REAL record
`_rl[!idx]`, and lowers `it.n` to the native projection `(!it).n` (the mirror
`ConcurrencyChecker.summary` shape). The contract's `self.items[i].n` is the same native
projection. Before S-C4 the loop took the opaque `iter_length : int -> int` and failed L3-tc
(`array item` vs `int`). The postcondition holds only through the element connection:
every element's `n` is non-negative, so the running sum is.
"""
# pycsl-expected: FAIL
from __future__ import annotations
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Item:
    name: str
    n: int = 0


class Bag:
    def __init__(self, k: int) -> None:
        self.k = k
        self.items: List[Item] = []

    #@ ensures \length(self.items) == \old(\length(self.items)) + 1
    #@ assigns self.items
    def add(self, name: str, n: int) -> None:
        self.items.append(Item(name=name, n=n))

    #@ requires \forall i; 0 <= i and i < \length(self.items) ==> self.items[i].n >= -1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def total(self) -> int:
        t = 0
        #@ loop invariant t >= 0
        for it in self.items:
            t += it.n
        return t
