r"""Test 0966 — a MUTUALLY RECURSIVE method group emits a single WhyML `let rec ... with ...`
chain, and a recursive-descent cursor discharges its termination measure.

Two independent things are pinned here.

1. THE `with` CONTINUATION.  Module 6 detects a multi-function SCC and chains the
   non-opening members onto the group's `let rec`.  For PURE/logic functions it used
   WhyML's `with function` continuation, which is correct; for PROGRAM functions it
   emitted OCaml's `and`, which WhyML does not accept:

       let rec f (n: int) : int = ... g ...
       and g (n: int) : int = ...          (* "unbound function or predicate symbol 'g'" *)

   and, with a `variant` clause present, it fails even earlier with "unexpected
   'variant' clause".  No emitted file had ever reached that branch (0 of 52
   self-annotation mirrors and 0 of 812 corpus programs contained an `and`
   continuation), so the defect was invisible: mutual recursion looked supported when
   read in the emitter and was in fact unreachable.  The group below is the regression
   test that keeps the branch exercised.

2. THE DESCENT TERMINATION MEASURE.  A recursive-descent parser's precedence chain
   calls DOWN a level without consuming a token, so `\length(self.toks) - self.pos`
   does NOT decrease along the descent and cannot be the whole measure.  The
   well-founded order is lexicographic — (tokens remaining, precedence level) — and
   PyCSL's `#@ \variant (<expr>, <ordering>)` form is a well-founded RELATION, not a
   tuple.  The measure is therefore ENCODED IN ONE INTEGER:

       #@ \variant 16 * (\length(self.toks) - self.pos) + <level>

   with the level bounded by the multiplier, so consuming a token dominates any rise
   in level.  `top` (level 3) descends to `mid` (level 2) with the cursor unmoved —
   the first component is equal and the second strictly decreases; `mid` recurses back
   up to `top` only AFTER `take` has consumed a token — the first component strictly
   decreases and the level is free to rise.  Both `variant decrease` goals are proved.

   NOTE the surface gotcha this test also documents: a LEADING parenthesis
   (`#@ \variant (`) is parsed as the `(expr, ordering)` structural-variant form and
   is a syntax error, so the multiplier is written first.

The class invariant `self.pos <= \length(self.toks)` is what makes the measure
non-negative (Why3's variant VC requires it), and `take`'s `ensures` is what makes it
strictly decrease.  Both are genuine facts about the cursor, not proof conveniences.
"""
from typing import List
from dataclasses import dataclass


@dataclass
class Token:
    kind: str
    value: str


def mutable_state(cls):
    return cls


#@ class invariant 0 <= self.pos
#@ class invariant self.pos <= \length(self.toks)
@mutable_state
class P:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, tokens: List[Token]) -> None:
        self.toks: List[Token] = tokens
        self.pos: int = 0

    #@ requires self.pos < \length(self.toks)
    #@ ensures self.pos == \old(self.pos) + 1
    #@ assigns self.pos
    def take(self) -> Token:
        t = self.toks[self.pos]
        self.pos += 1
        return t

    #@ requires True
    #@ ensures self.pos >= \old(self.pos)
    #@ assigns self.pos
    #@ \variant 16 * (\length(self.toks) - self.pos) + 3
    def top(self) -> int:
        return self.mid()

    #@ requires True
    #@ ensures self.pos >= \old(self.pos)
    #@ assigns self.pos
    #@ \variant 16 * (\length(self.toks) - self.pos) + 2
    def mid(self) -> int:
        if self.pos < len(self.toks):
            self.take()
            return self.top()
        return 0
