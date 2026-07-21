r"""Test 0934 — FAITHFUL NEGATIVE LITERAL ARRAY INDEX (W8 capability (iv)).

Python's `a[-k]` reads the k-th element FROM THE END: `a[len(a) - k]`. PyCSL used to
lower the index literally, emitting `a[(- 1)]`. That was wrong twice over:

  * UNFAITHFUL — WhyML/Why3 arrays are 0-indexed with no from-the-end convention, so
    `a[-1]` denotes nothing the Python program ever reads; and
  * UNPROVABLE — the array-bounds VC `0 <= i < Array.length a` can NEVER be discharged
    for a negative `i`, so every such read was a permanently red goal (and, in a
    `\trusted` stub, an invisible one).

This test pins the repair: a syntactically NEGATIVE INTEGER LITERAL index on an
array-typed base lowers to `a[Array.length a - k]`, and the bounds obligation then
discharges from the ordinary length precondition / class invariant.

    last          self.toks[-1]   ->  self.toks[((Array.length self.toks) - 1)]
    tail          a[-1]           ->  (a)[((Array.length a) - 1)]
    tail2         a[-2]           ->  (a)[((Array.length a) - 2)]

SCOPE / HONEST RESIDUAL. Only a *literal* `-k` is recognised. A negative value carried
in a VARIABLE is not statically detectable and keeps the old lowering; modelling it
needs a conditional (`if i < 0 then len + i else i`) read, which is a separate
capability. Nothing here assumes anything about run-time negative variables.

NON-VACUITY / ANTI-FACADE. Each function has a falsifiable VALUE postcondition that
names the from-the-end cell EXPLICITLY through the positive index:

    tail:  ensures \result == a[\length(a) - 1]
    tail2: ensures \result == a[\length(a) - 2]

A lowering that dropped the read, returned an unconstrained value, or picked the WRONG
cell cannot discharge these. `last_agrees` is the record/class-invariant twin: it reads
the SAME cell once via `[-1]` and once via `[\length - 1]` and asserts they agree
(`\result == 1`); the evil twin `\result == 0` does not prove. `off_by_one_differs`
is the discriminating control — it compares `[-1]` against `[-2]` on a two-element
array whose ends differ, so a lowering that collapsed every negative index to the same
cell would fail it.

BOUNDS come only from what the live code genuinely maintains — `\length(a) >= 1`
(resp. `>= 2`) as a precondition, and the class invariant `\length(self.toks) >= 1`
for the record case. No `#@ no_exception`, no convenience narrowing.

No new axiom, no abstract val: `Array.length` is Why3 stdlib.
"""
from typing import List


def mutable_state(cls):
    return cls


class Tok:
    def __init__(self, py_type, string):
        self.py_type: int = py_type
        self.string: str = string


#@ requires \length(a) >= 1
#@ ensures \result == a[\length(a) - 1]
#@ assigns \nothing
def tail(a: List[int]) -> int:
    return a[-1]


#@ requires \length(a) >= 2
#@ ensures \result == a[\length(a) - 2]
#@ assigns \nothing
def tail2(a: List[int]) -> int:
    return a[-2]


#@ requires \length(a) >= 2
#@ requires a[\length(a) - 1] != a[\length(a) - 2]
#@ ensures \result == 1
#@ assigns \nothing
def off_by_one_differs(a: List[int]) -> int:
    if a[-1] != a[-2]:
        return 1
    return 0


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
@mutable_state
class Parser:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0

    #@ requires True
    #@ ensures \result == self.toks[\length(self.toks) - 1]
    #@ assigns \nothing
    def last(self) -> Tok:
        return self.toks[-1]

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def last_agrees(self) -> int:
        n = len(self.toks)
        if self.toks[-1].py_type == self.toks[n - 1].py_type:
            return 1
        return 0


if __name__ == "__main__":
    assert tail([7, 8, 9]) == 9
    assert tail2([7, 8, 9]) == 8
    assert off_by_one_differs([7, 9]) == 1
    p = Parser([Tok(55, "+"), Tok(1, "x")])
    assert p.last().py_type == 1
    assert p.last_agrees() == 1
