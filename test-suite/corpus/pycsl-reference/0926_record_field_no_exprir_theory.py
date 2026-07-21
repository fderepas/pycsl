"""Test 0926 — a record-typed class field does NOT drag in the `emit_ir` ADT theory.

parser-primitives-wall-impl-3.md capability (i) (the LOW-BLAST-RADIUS record-element
class-field gate). 0925 established the FIELD TYPING (`self.toks: List[Tok]` → `mutable
toks: array tok`). This test pins the GATE that carries it: the only route to a
record-typed self-field is `@mutable_state`, which used to ALSO emit the whole ~277-line
`emit_ir` ADT theory (the 80-constructor sum + `kind_of` + every projector/discriminant +
the recursive `size` and its size-decrease lemmas + `irlist`/`iropt`) into the file — dead
weight in every VC's SMT context, and the measured blast radius that made `@mutable_state`
unaffordable on a big mirror file. The theory is now DEFERRED when the coarse
`@mutable_state` disjunct is the only trigger, and spliced back in only if the emitted text
actually references a symbol it declares. A `_Parser`-shaped token cursor references none,
so it emits as a bare record + cursor: 26 lines instead of 303.

The cursor read `self.toks[self.i]` returns a real `tok` (not `int`), and its
out-of-bounds obligation discharges via the class invariant — the `by`-witness for the
`array tok` field is `Array.make 1 { py_type = 0; ... }` (a record literal).

NON-VACUITY: `first_type` is the evil twin's control — it reads element 0 of a param
array and its `ensures` names the FAITHFUL projection, so a facade lowering (an opaque
`get_py_type` / an `int`-collapsed element) cannot prove it. No new axiom (record + array
are Why3 stdlib).
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

    # The cursor primitive: a record-typed read off a record-typed class field.
    # Returns `tok`, and the array-read OOB VC is discharged by the class invariant.
    #@ requires True
    #@ ensures True
    def cur(self) -> Tok:
        return self.toks[self.i]


#@ requires \length(toks) >= 1
#@ ensures \result == toks[0].py_type
def first_type(toks: List[Tok]) -> int:
    return toks[0].py_type


if __name__ == "__main__":
    p = Parser([Tok(1, "x", 0, 1)])
    t = p.cur()
    assert first_type([Tok(1, "x", 0, 1)]) == 1
