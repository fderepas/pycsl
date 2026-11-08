r"""Test 5113 -- gen #37 route #226 increment 2c CONTROL (expected PASS): the mirror `proof2why3/parser._Parser` shape, `self.pos <= \length(self.toks)` with `self.pos = 0` and NO `#@ requires` — true for EVERY list, so the premise-free goal `forall toks : array int, pos : int. toks = toks -> pos = 0 -> (pos <= Array.length toks)` PROVES. CPython `remaining(Cur([]))` is 0.
"""

from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant 0 <= self.pos
#@ class invariant self.pos <= \length(self.toks)
@mutable_state
class Cur:
    def __init__(self, toks: List[Tok]) -> None:
        self.toks: List[Tok] = toks
        self.pos: int = 0


#@ ensures \result >= 0
#@ assigns \nothing
def remaining(p: Cur) -> int:
    return len(p.toks) - p.pos


if __name__ == "__main__":
    assert remaining(Cur([])) == 0
    assert remaining(Cur([Tok(1)])) == 1
