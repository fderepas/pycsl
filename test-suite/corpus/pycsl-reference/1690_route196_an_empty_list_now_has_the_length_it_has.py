r"""Test 1690 - ROUTE #196 control (gen #30): the repair is FAITHFUL, not merely opaque. With the empty-list placeholder substituted by the genuinely EMPTY array at the call boundary, the caller now proves CPythons OWN answer - `len([])` is 0 - which it could NOT prove before (the model insisted on 1024). A repair that only made the length undecided would leave this unproven; this one restores the right value.
"""
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
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self) -> int:
        return self.g([])
