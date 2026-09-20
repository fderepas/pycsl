r"""Test 1686 - ROUTE #194 control (gen #30): making the erased-collection placeholder opaque costs an ORDINARY int actual nothing. A genuine `0` still reaches the same int-erased parameter and the same callee contract still discharges - the repair removes a value the model never had, not one it did.
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
    #@ ensures p == 0 ==> \result == 1
    #@ assigns \nothing
    def f(self, p) -> int:
        if p == 0:
            return 1
        return 2

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def probe(self) -> int:
        return self.f(0)
