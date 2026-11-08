r"""Test 1685 - ROUTE #194 carrier (gen #30): an ARRAY-shaped actual reaching an INT-ERASED parameter was replaced by the literal `0`, and the callee's contract READ that zero. `_coerce_to_int` answers `"0"` for any actual whose lowered text starts with `(sorted_1 `, `(Array.make`, `(array_slice `, ... The argument-coercion plane's baseline said this "DECIDES nothing ... the receiving param is int-erased, so no law reads it" - but a CONTRACT on an int-erased param IS a law that reads it. `self.f(sorted(xs))` emitted `(p__f self 0)`, the array discarded entirely (Why3 warns "unused variable xs"), and the callee's `ensures p == 0 ==> \result == 1` - TRUE of its own body - discharged `\result == 1` while CPython answers 2. The placeholder is now Why3's `(any int)`, so the erased collection stands for EVERY int and decides nothing.
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
        xs: List[int] = [3, 1, 2]
        return self.f(sorted(xs))
