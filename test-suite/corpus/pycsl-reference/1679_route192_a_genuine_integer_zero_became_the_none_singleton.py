r"""Test 1679 - ROUTE #192 carrier (gen #30): a GENUINE integer `0` passed to an `Optional[<record>]` parameter was silently re-tagged as the Python `None`. The lift in `_option_record_param_upgrade`'s sibling recognised the `None` actual by its WhyML SPELLING `"0"`, which is what the typed `NoneExpr` arm used to answer - so an actual that really WAS the integer 0 lowered to `(None: option tok)` and the callee's `start == None ==> \result == 1` discharged in the caller. `self.tag(0)` PROVED `\result == 1` while CPython returns 2. Route #191 is what makes the two distinguishable: `None` now spells itself `pycsl_none`, so `"0"` can only be a real int, and the arm is removed. The call is REFUSED (an int is not an `option tok`) instead of answered wrongly.
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
        return self.tag(0)
