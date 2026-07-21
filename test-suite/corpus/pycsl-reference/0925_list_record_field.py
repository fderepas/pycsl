"""Test 0925 — a `List[<record>]` CLASS FIELD is `array <record>` (not `array int`).

parser-primitives-wall-impl-2.md Gate S. A stateful class field annotated
`self.toks: List[Tok]` lowers to `mutable toks: array tok` (the element record is
PRESERVED, not erased to `array int`), so a field-array read `self.toks[self.i]`
returns a real `tok` record and a projection `self.toks[self.i].py_type` reads the
faithful `int` field — not the opaque `int` collapse. The out-of-bounds obligation on
the read discharges via the class invariant `0 <= self.i < \length(self.toks)`, and the
record's array `by`-witness is `Array.make N { py_type = 0; ... }` (a record literal, not
the int `0`). The element record is emitted PURE (Why3 forbids a mutable array element).
No new axiom (record + array are Why3 stdlib).
"""
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    py_type: int
    string: str
    start: int
    end: int


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
@mutable_state
class Parser:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0

    #@ requires True
    #@ ensures True
    def cur(self) -> Tok:
        return self.toks[self.i]


#@ requires 0 <= i and i < len(toks)
#@ ensures \result == toks[i].py_type
def elem_type(toks: List[Tok], i: int) -> int:
    return toks[i].py_type


if __name__ == "__main__":
    p = Parser([Tok(1, "x", 0, 1)])
    t = p.cur()
    assert elem_type([Tok(1, "x", 0, 1)], 0) == 1
