r"""Test 5246 -- gen #37 route #385 (expected FAIL): `self.toks = toks; toks.extend(..)` under `\length <= 1`: PROVED at the store; now REFUSED (R384; CPython count 4). PROVED at base 0a2d8019b.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant \length(self.toks) <= 1
@mutable_state
class Cur:
    #@ requires len(toks) <= 1
    def __init__(self, toks: List[Tok]) -> None:
        self.toks: List[Tok] = toks
        toks.extend(toks)
        toks.extend(toks)


#@ ensures \result <= 1
#@ assigns \nothing
def count(p: Cur) -> int:
    return len(p.toks)


if __name__ == "__main__":
    r = count(Cur([Tok(1)]))
    print("VIOLATION count =", r) if r > 1 else print("no violation")
