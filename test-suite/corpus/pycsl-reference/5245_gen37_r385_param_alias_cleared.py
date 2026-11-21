r"""Test 5245 -- gen #37 route #385 (expected FAIL): `self.toks = toks; toks.clear()` under `\length >= 1`: the goal bound the field at its store and PROVED; now REFUSED (R384: a call after the PARAM store; CPython IndexError). PROVED at base 0a2d8019b.
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
        toks.clear()

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
