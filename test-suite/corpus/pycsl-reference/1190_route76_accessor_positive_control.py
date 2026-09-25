"""1190 — ROUTE #76 POSITIVE CONTROL: the accessor idiom must still prove.

The repair is a fail-closed ALLOWLIST, not a blanket refusal, and this is the shape it
exists to preserve. `cur` returns THE object held in the slot — not a copy — so
`\\result == self.toks[self.i]` is TRUE under Python's identity `==` and must remain
provable. Five reference locks (0900, 0901, 0929, 0933, 0934) carry exactly this idiom;
without this control a blanket refusal of class-typed `==` would silently cost all five.

The allowlist admits it because EVERY `return` in the function returns syntactically that
same pure READ PATH. A read path denotes the same object each time it is evaluated; a
CALL does not, which is why a constructor operand is excluded (see 1192).
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from typing import List


# (#49) gen #31 — `@mutable_state` was USED below and DEFINED NOWHERE, so this
# `# pycsl-expected: PASS` driver raised `NameError` at import: not one function
# that fails, the whole module. Its siblings 0748, 0750 and 0751 all carry exactly
# these three lines. Found by a sweep that asks only "does this file LOAD", which
# is a question no instrument here had ever asked on its own.
def mutable_state(cls):
    return cls


class Tok:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, py_type):
        self.py_type: str = py_type


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
@mutable_state
class Cursor:
    #@ \trusted reviewer: pycsl-reference-1190
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
