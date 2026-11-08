"""Test 0901 — NEGATIVE twin of 0900 (self-field subscript projection floor). # pycsl-expected: FAIL

Two claims that must BOTH stay unproven, or 0900's green is a facade:

  * `at_op` — `\\result != False ==> self.toks[self.i].py_type == "EOF"` is FALSE of
    the faithful lowering (`at_op` is true exactly when the current token's kind
    is `"OP"`). If it ever PASSES, `self.f[i].sub` has collapsed to a constant, or
    the `str` element field has been erased to an unconstrained int where every
    literal comparison is satisfiable.

  * `skip_ops` — the SAME loop as 0900 but with the EOF-sentinel class invariant
    REMOVED. Without it nothing bounds `self.i` away from the last index, so
    `advance` may stutter and the variant `\\length(self.toks) - self.i` need not
    decrease: the termination VC must stay unproven. If it ever PASSES, the
    sentinel invariant is not load-bearing and 0900 proves termination by some
    route other than the lexer's real EOF guarantee.
"""
# pycsl-expected: FAIL
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
@mutable_state
class Cursor:
    #@ \trusted reviewer: pycsl-reference-0901
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
    #@ ensures \result != False ==> self.toks[self.i].py_type == "EOF"
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
        #@ loop variant \length(self.toks) - self.i
        while self.at_op('+', '-'):
            self.advance()
            n = n + 1
        return n
