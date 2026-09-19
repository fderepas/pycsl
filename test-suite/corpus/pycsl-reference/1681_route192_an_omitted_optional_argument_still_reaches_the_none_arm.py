r"""Test 1681 - ROUTE #192 control (gen #30): removing the `"0"` spelling from the two lifts costs the LEGITIMATE cases nothing. An OMITTED optional argument still reaches the union's `None` arm, because after route #191 the Python `None` default arrives spelled `pycsl_none` - which is the whole point: the lift now recognises the value, not the accident that it used to share a spelling with the integer 0.
"""
from typing import List, Optional

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
class Parser:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0

    #@ requires True
    #@ ensures value == None ==> \result == 1
    #@ assigns \nothing
    def expect(self, kind: str, value: Optional[str] = None) -> int:
        if value is None:
            return 1
        return 2

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def probe(self) -> int:
        return self.expect("RPAREN")
