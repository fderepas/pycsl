"""Test 0927 — the token-cursor `advance` primitive on a record-typed class field.

W8 conversion wave W1 (`parser-primitives-wall-impl-3.md`). 0925 pinned the FIELD
TYPING (`self.toks: List[Tok]` → `mutable toks: array tok`) and 0926 pinned the
low-blast-radius GATE that carries it. This test pins the three increments that the
LIVE mirror shape needs on top of them, all of which 0925/0926 sidestepped by using a
`@dataclass` element with only scalar fields:

1. ELEMENT RECORD BY DECLARATION. The live token class is a plain class whose fields
   are declared by annotated `__init__` assignments (`self.type: int = t.type`), NOT a
   `@dataclass`/`NamedTuple`/positional-ctor record. `_collect_class_fields` already
   emits exactly such a class as a record `type_decl`, so the `List[<it>]` element
   pre-scan now recognizes it too — `toks` is `array _tok`, not the element-erased
   `array int`.

2. TRANSITIVE ELEMENT PURITY + a NESTED record witness. `Tok.start`/`Tok.end` are
   `Tuple[int, int]` slots, which synthesize their own `pytuple_int_int` record. Why3
   forbids a MUTABLE element inside `array`, and mutability is INFECTIOUS through a
   record field — so the pinned-pure element record's own record-typed fields must be
   emitted pure as well, and the `by` witness needs a NESTED record literal
   (`start = { field0 = 0; field1 = 0 }`), not the scalar `0`.

3. THE CURSOR STEP. `len(self.toks)` is `Array.length` (the opaque
   `iter_length : int -> int` fallback mistypes against `array tok`), and the local
   `t = self.toks[self.i]` is RECORD-typed, so it pre-declares a record ref rather
   than the integer `ref 0`.

`advance` returns the current token and steps the cursor. Its interesting obligation is
the CLASS INVARIANT: `self.i` may only be incremented while `self.i < len - 1`, so
`0 <= self.i < len(self.toks)` is re-established at exit (drop the guard and the type
invariant fails). The array read discharges from the same invariant.

NON-VACUITY: `second_type` is the control — it reads element 1 of a param array and its
`ensures` names the FAITHFUL projection, so an element-erased or opaque-getter lowering
cannot prove it. No new axiom (record + array are Why3 stdlib).
"""
from typing import List, Tuple


def mutable_state(cls):
    return cls


class Tok:
    def __init__(self, py_type, string, start, end):
        self.py_type: int = py_type
        self.string: str = string
        self.start: Tuple[int, int] = start
        self.end: Tuple[int, int] = end


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
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[self.i]

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def advance(self) -> Tok:
        t = self.toks[self.i]
        if self.i < len(self.toks) - 1:
            self.i += 1
        return t


#@ requires \length(toks) >= 2
#@ ensures \result == toks[1].py_type
def second_type(toks: List[Tok]) -> int:
    return toks[1].py_type


if __name__ == "__main__":
    p = Parser([Tok(1, "x", (1, 0), (1, 1)), Tok(55, "+", (1, 1), (1, 2))])
    assert p.cur().py_type == 1
    assert p.advance().py_type == 1
    assert p.cur().py_type == 55
    assert second_type([Tok(1, "x", (1, 0), (1, 1)),
                        Tok(55, "+", (1, 1), (1, 2))]) == 55
