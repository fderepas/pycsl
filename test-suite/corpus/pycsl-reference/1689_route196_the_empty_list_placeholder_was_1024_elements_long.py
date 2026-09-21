r"""Test 1689 - ROUTE #196 carrier (gen #30): the EMPTY-LIST placeholder is 1024 ELEMENTS LONG, and a callee's contract can READ that length. `[]` lowers to the emitter's `(Array.make 1024 0)` stand-in; passed through unchanged to an `array int` param, a sibling `def g(self, ns: List[int]) -> int: return len(ns)` carrying `ensures \result == \length(ns)` - TRUE of its own body - handed the CALLER `\result == 1024` for `self.g([])`, which PROVED while CPython answers 0. Route #159 corrected this same placeholder's `in_bounds` obligation with a post-hoc rewrite of the emitted text; that is about INDEXING and says nothing about LENGTH at a call boundary. The faithful value is the genuinely EMPTY array, which is what the `array emit_ir` arm beside it already substituted.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


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
class P:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0

    #@ requires True
    #@ ensures \result == \length(ns)
    #@ assigns \nothing
    def g(self, ns: List[int]) -> int:
        return len(ns)

    #@ requires True
    #@ ensures \result == 1024
    #@ assigns \nothing
    def probe(self) -> int:
        return self.g([])
