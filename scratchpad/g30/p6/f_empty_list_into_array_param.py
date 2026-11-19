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
