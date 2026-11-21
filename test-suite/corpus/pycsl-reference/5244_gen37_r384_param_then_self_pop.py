r"""Test 5244 -- gen #37 route #384 (expected FAIL): `self.toks = toks; self.toks.pop()` under `\length(self.toks) >= 1`: no goal, assumed; now REFUSED (PYCSL-R384-INVARIANT-GOAL-UNSTATABLE; CPython IndexError). PROVED at base 0a2d8019b.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant \length(self.toks) >= 1
@mutable_state
class Cur:
    #@ requires len(toks) >= 1
    def __init__(self, toks: List[Tok]) -> None:
        self.toks: List[Tok] = toks
        self.toks.pop()

    #@ no_exception \all
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[0]


if __name__ == "__main__":
    try:
        Cur([Tok(7)]).cur()
        print("no violation")
    except IndexError as e:
        print("VIOLATION IndexError", e)
