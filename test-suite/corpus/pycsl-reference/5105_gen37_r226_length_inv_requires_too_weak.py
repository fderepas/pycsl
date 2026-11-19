r"""Test 5105 -- gen #37 route #226 increment 2c (expected FAIL): `#@ requires len(toks) >= 1` on `__init__` but the invariant claims `\length(self.toks) >= 2`. The premise is kept and is too weak: `forall toks : array tok. toks = toks -> (Array.length toks >= 1) -> (Array.length toks >= 2)` FAILS. PROVED at base; CPython `n(P([Tok(1)]))` is 1.
"""
# pycsl-expected: FAIL
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
    #@ requires len(toks) >= 1
    def __init__(self, toks: List[Tok]) -> None:
        self.toks: List[Tok] = toks


#@ ensures \result >= 2
#@ assigns \nothing
def n(p: P) -> int:
    return len(p.toks)


if __name__ == "__main__":
    assert n(P([Tok(1)])) == 1
