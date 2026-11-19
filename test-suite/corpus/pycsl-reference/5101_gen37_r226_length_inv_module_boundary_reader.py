r"""Test 5101 -- gen #37 route #226 increment 2c (expected FAIL): the MODULE-BOUNDARY shape over a list field (corpus 2220 before its `#@ requires` was added). A reader `count(p)` publishes `ensures \result >= 1` from `\length(self.toks) >= 1`; no construction in the file. PROVED at base; CPython `count(Parser([]))` is 0.
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


#@ ensures \result >= 1
#@ assigns \nothing
def count(p: Parser) -> int:
    return len(p.toks)


if __name__ == "__main__":
    assert count(Parser([])) == 0
