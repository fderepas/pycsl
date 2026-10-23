r"""Test 1687 - ROUTE #195 carrier (gen #30): the EMPTY-LIST placeholder reaching an INT-ERASED parameter was substituted with the literal `0`, and the callee's contract READ that zero. The argument-coercion plane's baseline said the substitution "loses nothing the placeholder had ... and the callee is a `\trusted` `val` with `ensures true`, so NO property of the argument is provable on either side". The callee does not have to be `\trusted` and does not have to say `ensures true`: `def f(self, p)` (un-annotated param, so the emitted `val` declares `p: int`) carrying `ensures p == 0 ==> \result == 1` - TRUE of its own body - called as `self.f([])` emitted `(p__f self 0)` and PROVED `\result == 1` while CPython answers 2, because `[] == 0` is False. The substitution is now Why3's `(any int)`: there is no int that represents a list, so the model must not name one.
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
        return self.f([])
