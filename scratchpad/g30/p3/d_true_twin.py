from typing import List, Optional


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
class Parser:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0

    # TRUE of its own body: it returns 1 exactly when `start` is the None singleton.
    #@ requires True
    #@ ensures start == None ==> \result == 1
    #@ assigns \nothing
    def tag(self, start: Optional[Tok]) -> int:
        if start is None:
            return 1
        return 2

    # the carrier: a GENUINE integer 0 flows into the Optional[<record>] slot
    #@ requires True
    #@ ensures \result == 2
    #@ assigns \nothing
    def probe(self) -> int:
        return self.tag(0)
