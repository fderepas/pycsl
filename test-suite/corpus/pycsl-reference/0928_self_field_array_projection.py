r"""Test 0928 — self-field array-read record PROJECTION (W8 capability (iii)).

0925 pinned the FIELD TYPING (`self.toks: List[Tok]` → `mutable toks: array tok`),
0926 the low-blast-radius gate that carries it, and 0927 the cursor step
(`t = self.toks[self.i]`, `len(self.toks)`). All three stop SHORT of reading a FIELD
off the element: before this test, `self.toks[self.i].py_type` lowered to the opaque
`(get_py_type self.toks[self.i])` and `t.py_type` (on the record-typed local) to
`(get_py_type !t)`. Both FAIL L3-tc — `This expression has type PyCSL_Program.tok, but
is expected to have type int` — because the abstract getter is declared `int -> int`
while its argument is the element record. The `let _rec_ = <arr>[i] in _rec_.<field>`
projector was wired for a PARAM / record-array-LOCAL base only; a SELF-FIELD base fell
through to the abstract-op fallback.

This test pins BOTH halves of the fix:

1. DIRECT — `self.toks[self.i].py_type` / `.string`: the `Subscript` base is a
   `FieldGet`/`Attribute` on `self` naming a field in `_record_array_fields`
   (field -> element record class, populated by `_emit_type_decls` only for a
   `List[<record>]` record field), so it takes the same `_rec_` projector as a param
   array read. Both an `int` field and a `string` field project natively — no
   `get_py_type`, no `str_hash_op`, no int-erasure.

2. LOCAL-BOUND — `t = self.toks[self.i]` then `t.py_type`: such a local is pre-declared
   as a record REF (0927), so its projection is `(!t).py_type`.

BOUNDS: every array read is discharged by the class invariant
`0 <= self.i < \length(self.toks)` — no `#@ no_exception`, no requires-side narrowing.

NON-VACUITY / ANTI-FACADE. `direct_matches_local` and `texts_match` are the controls:
each reads the SAME element ONCE through the DIRECT path and ONCE through the
LOCAL-BOUND path and its `ensures \result == 1` says the two agree. That postcondition
is falsifiable (flip it to `\result == 0` and it is Unknown) and it can only be
discharged when BOTH lowerings are the real `Array.get` + record projection over the
same `toks`/`i`; an opaque getter on either side severs the link (and in fact does not
even type-check). `second_type` keeps 0927's param-path control, whose `ensures` names
the faithful projection directly.

No new axiom (record + array are Why3 stdlib); no abstract val for the token kind — the
compared token kind is the CONCRETE int literal 55 (`tokenize.OP`).
"""
from typing import List


def mutable_state(cls):
    return cls


class Tok:
    def __init__(self, py_type, string):
        self.py_type: int = py_type
        self.string: str = string


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
    def kind(self) -> int:
        return self.toks[self.i].py_type

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def text(self) -> str:
        return self.toks[self.i].string

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def local_kind(self) -> int:
        t = self.toks[self.i]
        return t.py_type

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def direct_matches_local(self) -> int:
        t = self.toks[self.i]
        if self.toks[self.i].py_type == t.py_type:
            return 1
        return 0

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def texts_match(self) -> int:
        t = self.toks[self.i]
        if self.toks[self.i].string == t.string:
            return 1
        return 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def is_op(self) -> int:
        t = self.toks[self.i]
        if t.py_type == 55:
            return 1
        return 0


#@ requires \length(toks) >= 2
#@ ensures \result == toks[1].py_type
def second_type(toks: List[Tok]) -> int:
    return toks[1].py_type


if __name__ == "__main__":
    p = Parser([Tok(55, "+"), Tok(1, "x")])
    assert p.kind() == 55
    assert p.text() == "+"
    assert p.local_kind() == 55
    assert p.direct_matches_local() == 1
    assert p.texts_match() == 1
    assert p.is_op() == 1
    assert second_type([Tok(1, "x"), Tok(55, "+")]) == 55
