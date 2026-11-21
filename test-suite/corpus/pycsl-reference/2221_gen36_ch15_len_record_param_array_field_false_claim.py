r"""Test 2221 — ch15 crash fix (expected FAIL): `len(p.toks)` is the real array length, not
a constant. CPython: `count(Parser([Tok(1), Tok(2)]))` is 2, so `\result == 1` is false and
must stay unproved (the class invariant only gives `\length(p.toks) >= 1`). Control: 2220.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
@mutable_state
class Parser:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0


#@ ensures \result == 1
#@ assigns \nothing
def count(p: Parser) -> int:
    return len(p.toks)


if __name__ == "__main__":
    assert count(Parser([Tok(1), Tok(2)])) == 2
