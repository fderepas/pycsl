"""Test 0900 — contract SELF-FIELD subscript projection `self.f[i].sub` (POSITIVE).

The element-projection production `<collection>[<idx>].<field>` (§3.1.4c) with a
SELF-FIELD base. Before this, only a plain `CNAME` base (`a[i].x`) and `\\result`
(`\\result[i].x`) parsed; `self.toks[\\length(self.toks) - 1].py_type` was rejected
by the contract grammar ("unexpected trailing input").

What the fixture LOCKS, end-to-end:

  * the form PARSES in a class invariant, in an `ensures`, and in a
    `loop invariant`;
  * it LOWERS to the native record projection over the array read
    (`(let _rec_ = toks[..] in _rec_.py_type)`), NOT the unbound abstract getter
    `get_py_type` — an unbound symbol fails the whole file;
  * the record's `by {}` inhabitance witness is PINNED by the invariant
    (`Array.make 1 { py_type = "EOF"; ... }`), so a genuine sentinel invariant is
    exhibitable rather than vacuously unsatisfiable;
  * the property it exists for DISCHARGES: the `while self.at_op(...)` cursor
    loop TERMINATES, because the EOF sentinel at the last index forces
    `self.i < len - 1` whenever the loop condition holds, so `advance` really
    increments and the variant `\\length(self.toks) - self.i` strictly decreases.

This is the `_ContractParser` cursor shape of `src/pycsl/frontend/Module2_Parser.py`.
"""
# pycsl-expected: PASS
from typing import List


def mutable_state(cls):
    return cls


class Tok:
    __slots__ = ('type', 'string')

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, type_, string):
        self.type: str = type_
        self.string: str = string


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
#@ class invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
@mutable_state
class Cursor:
    #@ \trusted reviewer: pycsl-reference-0900
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0

    #@ requires True
    #@ ensures \result == self.toks[self.i]
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[self.i]

    #@ requires True
    #@ ensures \old(self.i) < \length(self.toks) - 1 ==> self.i == \old(self.i) + 1
    #@ assigns self.i
    def advance(self) -> Tok:
        t = self.toks[self.i]
        if self.i < len(self.toks) - 1:
            self.i += 1
        return t

    #@ requires True
    #@ ensures \result != False ==> self.toks[self.i].py_type == "OP"
    #@ assigns \nothing
    def at_op(self, *vals: str) -> bool:
        t = self.cur()
        return t.type == 'OP' and (not vals or t.string in vals)

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def skip_ops(self) -> int:
        n = 0
        #@ loop invariant 0 <= n
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_op('+', '-'):
            self.advance()
            n = n + 1
        return n
