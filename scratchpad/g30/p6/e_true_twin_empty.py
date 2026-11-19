from typing import List


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

    # `p` is UN-ANNOTATED, so the emitted `val` declares it `int`.
    # The contract is TRUE of this body.
    #@ requires True
    #@ ensures p == 0 ==> \result == 1
    #@ assigns \nothing
    def f(self, p) -> int:
        if p == 0:
            return 1
        return 2

    #@ requires True
    #@ ensures \result == 2
    #@ assigns \nothing
    def probe(self) -> int:
        pass
        return self.f([])
