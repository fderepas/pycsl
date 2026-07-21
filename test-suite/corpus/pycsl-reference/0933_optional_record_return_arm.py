r"""Test 0933 — `Optional[<record>]` RETURN gets a real RECORD ARM (W8 capability (v)).

The Union synthesizer lowered `-> Optional[R]` (R a declared record class) by dropping
the record arm as an unrecognised `Any` (GT1), collapsing the synthesized variant to the
vacuous

    type _union_peek_0 = Arm_0_None                 (* no payload arm at all *)

so `return self.toks[idx]` had nowhere to be injected and the emitted WhyML did not even
type-check:

    raise (Return__union_peek_0 self.toks[!idx])
    This expression has type tok, but is expected to have type _union_peek_0

Every `Optional[<record>]`-returning method was therefore permanently unverifiable — the
exact wall the parsers' `accept_op` / `accept_kw` / `peek` sat behind.

Now the arm is real and the return injects into it:

    type _union_peek_1 = Arm_1_0 tok | Arm_1_None
    raise (Return__union_peek_1 (Arm_1_0 self.toks[!idx]))
    raise (Return__union_peek_1 Arm_1_None)

The three return shapes the live cursors use are all covered:
  * `return self.toks[idx]`  — an element of the `array <record>` self-field  (`peek`);
  * `return self.advance()`  — a same-class sibling call declared `-> <record>`
                               (`accept_op` / `accept_kw`, on top of capability (vi));
  * `return None`            — the nullary arm (already worked).

ANTI-FACADE — no int erasure, machine-enforced. The arm's payload type is resolved
per record class, from the SAME registry Module 6 declares its records from: `peek`'s arm
carries `tok`, `find_node`'s carries `node`. A class that has NO emitted record type_decl
is deliberately NOT given an arm (it would silently resolve to the `int` default, i.e. a
new facade) and still degrades to `Any` exactly as before. There is no way for this test
to pass vacuously: with the old lowering the file does not TYPE-CHECK, so a dropped or
int-erased arm is a hard L3-tc failure, not a silent green.

NON-VACUITY — falsifiable VCs on both halves of the union-returning function:
  * `accept_op` carries the two-sided frame control `self.i >= \old(self.i)` and
    `self.i <= \old(self.i) + 1`. The first is provable ONLY because the None branch (which
    does not advance) is really emitted, and the second ONLY because the Some branch's
    `advance` really advances by at most one. The evil twin `self.i > \old(self.i)` — which
    a model that dropped the None branch WOULD prove — does not prove.
  * `peek`'s Some branch carries a genuine `index in array bounds` obligation on
    `self.toks[idx]`. It discharges from `idx < len(self.toks)` (the live guard) plus the
    precondition `offset >= 0`; DROP that precondition and the goal does not discharge.

PRECONDITION `offset >= 0` — genuine partiality, justified from the live body: `peek` reads
`self.toks[self.pos + offset]` under the guard `idx < len(self.toks)` ONLY. A negative
`offset` makes `idx` negative, which in Python silently reads from the END of the list —
a different element than the method claims to peek at. Every live call site passes a
non-negative literal. It is a partiality boundary, not a convenience narrowing.

No new axiom, no abstract val (`str_eq_op` is the pre-existing definition-by-`ensures`).
"""
from typing import List, Optional


def mutable_state(cls):
    return cls


class Tok:
    def __init__(self, py_type, string):
        self.py_type: int = py_type
        self.string: str = string


class Node:
    def __init__(self, tag, span):
        self.tag: int = tag
        self.span: int = span


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
#@ class invariant \length(self.nodes) >= 1
@mutable_state
class Parser:
    def __init__(self, toks: List[Tok], nodes: List[Node]):
        self.toks: List[Tok] = toks
        self.nodes: List[Node] = nodes
        self.i: int = 0

    #@ requires True
    #@ ensures \result == self.toks[self.i]
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[self.i]

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ ensures self.i <= \old(self.i) + 1
    #@ assigns self.i
    def advance(self) -> Tok:
        t = self.toks[self.i]
        if self.i < len(self.toks) - 1:
            self.i += 1
        return t

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def at_op(self, val: str) -> bool:
        t = self.cur()
        return t.string == val

    # shape 1 — `return <sibling call returning a record>` / `return None`
    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ ensures self.i <= \old(self.i) + 1
    #@ assigns self.i
    def accept_op(self, val: str) -> Optional[Tok]:
        if self.at_op(val):
            return self.advance()
        return None

    # shape 2 — `return self.<array-field>[idx]` / `return None`
    #@ requires offset >= 0
    #@ ensures True
    #@ assigns \nothing
    def peek(self, offset: int) -> Optional[Tok]:
        idx = self.i + offset
        if idx < len(self.toks):
            return self.toks[idx]
        return None

    # per-class arm typing: a SECOND record class gets its OWN arm payload type
    #@ requires k >= 0
    #@ ensures True
    #@ assigns \nothing
    def find_node(self, k: int) -> Optional[Node]:
        if k < len(self.nodes):
            return self.nodes[k]
        return None


if __name__ == "__main__":
    p = Parser([Tok(55, "+"), Tok(1, "x")], [Node(3, 9)])
    assert p.peek(0) is not None
    assert p.find_node(0) is not None
    assert p.accept_op("+") is not None
    assert p.accept_op("zzz") is None
