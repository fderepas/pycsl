r"""Test 1680 - ROUTE #192 carrier (gen #30), the `_union_*` twin: a GENUINE integer `0` passed to a synthesized-union parameter was substituted with the union's nullary `None` arm. The same spelling test (`arg.strip() in ("0","(0)")`) drives it, so `self.expect("RPAREN", 0)` lowered to `(Arm_0_None : _union_expect_0)` and PROVED `\result == 1` while CPython returns 2. Removed with its sibling; the call is REFUSED (an int is not a `_union_expect_0`).
"""
# pycsl-expected: FAIL
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
        return self.expect("RPAREN", 0)
