r"""Test 0929 — CONCRETE same-class sibling call with a RECORD return (W8 capability (vi)).

0926 pinned the low-blast-radius gate that types `self.toks: List[_Tok]` as
`array tok`, 0927 the cursor step (`t = self.toks[self.i]`, `advance`) and 0928 the
self-field array-read PROJECTION (`self.toks[self.i].py_type` -> the `_rec_` projector).
All three read the array DIRECTLY. The real parser shape does not: every predicate opens
with `t = self.cur()`, i.e. it projects a field off a SAME-CLASS SIBLING METHOD CALL.

Before this test that call was abstracted to a RECEIVER-LESS stub —
`val self_cur_0 () : int` — and the projection off it collapsed to an opaque
`val get_py_type (x: int) : int` getter. Two independent defects:

1. TYPE ERASURE. `_build_method_return_type_map` had no case for a `-> <RecordClass>`
   annotation, so `cur`'s return type was `int`. Every consumer then mistyped
   (`This expression has type PyCSL_Program.tok, but is expected to have type int`)
   and the file failed L3-tc.

2. RECEIVER LOSS — the FACADE. Even typed `: tok`, an abstract `val self_cur_0 () : tok`
   has NO link to the receiver: nothing relates its result to `self.toks[self.i]`, so no
   fact about the cursor reaches the caller. It is a stub that assumes an unconstrained
   token.

The fix lowers such a call to the CONCRETE sibling application `(parser__cur self)`.
That is SOUND — not an assumption — precisely because `cur` is a same-file VERIFIED
method: its body is emitted and its contract discharged in this very module, and the
class type invariant applies to the receiver it is passed. The callee-before-caller
emission order comes from the same SCC edge machinery the opt-in `#@ sibling_concrete`
callees use. The projection off the result is then a NATIVE record projection
(`let _rec_ = (parser__cur self) in _rec_.py_type`), and a `str`-typed field routes the
comparison through `str_eq_op` — no `get_py_type`, no `str_hash_op`, no int erasure.

NON-VACUITY / ANTI-FACADE. `sibling_agrees` is the decisive control: it compares the
SIBLING-CALL read against the DIRECT array read of the SAME cell and its
`ensures \result == 1` asserts they agree. That postcondition is falsifiable (flipping
it to `\result == 0` leaves the goal unproven) and it is discharged ONLY because
`cur`'s real `ensures \result == self.toks[self.i]` reaches this call site through the
concrete application. Replace the concrete call with ANY abstract `val` — typed or not —
and the two sides are unrelated and the goal fails. `texts_agree` is the same control on
the `string` field, so a hash-collapsed comparison cannot pass either.

`kind` / `at_eof` are the wave shapes this unlocks: a single-value predicate that
projects an int / a string field off `self.cur()`.

BOUNDS: every array read is discharged by the class invariant
`0 <= self.i < \length(self.toks)` — no `#@ no_exception`, no requires-side narrowing.
No new axiom (record + array are Why3 stdlib); no abstract val for the token kind — the
compared kind is the CONCRETE int literal 55 (`tokenize.OP`).
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
    #@ ensures \result == self.toks[self.i]
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[self.i]

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def kind(self) -> int:
        return self.cur().py_type

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def at_eof(self) -> int:
        if self.cur().string == "EOF":
            return 1
        return 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def at_op(self) -> int:
        if self.cur().py_type == 55:
            return 1
        return 0

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def sibling_agrees(self) -> int:
        if self.cur().py_type == self.toks[self.i].py_type:
            return 1
        return 0

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def texts_agree(self) -> int:
        if self.cur().string == self.toks[self.i].string:
            return 1
        return 0


if __name__ == "__main__":
    p = Parser([Tok(55, "+"), Tok(1, "x")])
    assert p.kind() == 55
    assert p.at_eof() == 0
    assert p.at_op() == 1
    assert p.sibling_agrees() == 1
    assert p.texts_agree() == 1
