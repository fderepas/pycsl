r"""Test 1682 - ROUTE #192 control (gen #30): an EXPLICIT `None` actual still lifts into an `Optional[<record>]` parameter's `option` type after the `"0"` spelling is removed, for the same reason as 1681 - it arrives as `pycsl_none`. Together 1681 and 1682 show the repair is a loss of the WRONG re-tagging only, not of the lift.
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
    #@ ensures start == None ==> \result == 1
    #@ assigns \nothing
    def tag(self, start: Optional[Tok]) -> int:
        if start is None:
            return 1
        return 2

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def probe(self) -> int:
        return self.tag(None)
