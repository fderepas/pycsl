"""Test 0980 — a MUTATING METHOD CALL on a `self.<field>` collection is REFUSED when the
lowering would erase it. It used to prove a postcondition that is FALSE of the program.

`self.xs.reverse()` had no recognizer, so it reached the generic abstract-op fallback in
`module6_whyml/expressions.py` and became

    val self_xs_reverse_0 () : int          <-- no `self`, no `writes`

— the mutation is not under-claimed, it is ABSENT. The method then satisfied
`#@ assigns \nothing`, satisfied the frame-preservation `ensures { self.xs = old self.xs }`
that #34 added for exactly this family (that clause is checked against the EMITTED body,
and the emitted body no longer contains the write), and RE-ESTABLISHED the class invariant
`self.xs[0] == 0`. Its caller's avatar `self_go_0 ()` was frameless too, so the caller
believed nothing had changed. Measured, before this refusal:

    #@ class invariant \length(self.xs) == 2
    #@ class invariant self.xs[0] == 0
    @mutable_state
    class C:
        #@ assigns self.xs
        def __init__(self) -> None:      self.xs: List[int] = [0, 7]
        #@ assigns \nothing
        def go(self) -> None:            self.xs.reverse()
        #@ ensures \result == 0                        <-- FALSE OF THE PROGRAM
        #@ assigns \nothing
        def run(self) -> int:            self.go(); return self.xs[0]

    [+] Verification SUCCESS! All contracts formally proven.

Real Python returns 7.

The refusal is gated on `not receiver_param and not writes_clause`, so it fires ONLY for an
abstract op that neither takes the receiver nor declares its writes; every recognizer-modelled
mutation is untouched. CENSUS: 0 in the 819-file reference corpus (2 `self.<f>.<mut>()` sites,
both modelled) and the corpus emission is BYTE-IDENTICAL across all 820 files.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ class invariant \length(self.xs) == 2
#@ class invariant self.xs[0] == 0
@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs: List[int] = [0, 7]

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def go(self) -> None:
        self.xs.reverse()

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def run(self) -> int:
        self.go()
        return self.xs[0]
