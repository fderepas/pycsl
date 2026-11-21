r"""Test 5111 -- gen #37 route #226 increment 2c CONTROL (expected PASS): the `#@ requires` is written `\length(tokens) >= 2` (an `ArrayLen` over the PARAMETER) and the field is bound to a parameter of a different name; the premise is kept. PROVES. CPython `n(P([Tok(1), Tok(2)]))` is 2.
"""
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant \length(self.toks) >= 2
@mutable_state
class P:
    #@ requires \length(tokens) >= 2
    def __init__(self, tokens: List[Tok]) -> None:
        self.toks: List[Tok] = tokens


#@ ensures \result >= 2
#@ assigns \nothing
def n(p: P) -> int:
    return len(p.toks)


if __name__ == "__main__":
    assert n(P([Tok(1), Tok(2)])) == 2
