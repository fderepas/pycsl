r"""Test 5110 -- gen #37 route #226 increment 2c CONTROL (expected PASS): 5106's cursor with `#@ requires len(toks) >= 1` on `__init__` (a `List[<record>]` parameter, so route #15's checking-only `__init` is not emitted). The premise establishes `0 <= i < len(toks)`: `forall toks : array tok, i : int. toks = toks -> i = 0 -> (Array.length toks >= 1) -> ..` PROVES. CPython: `Cur([Tok(7)]).cur().kind` is 7.
"""
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
class Cur:
    #@ requires len(toks) >= 1
    def __init__(self, toks: List[Tok]) -> None:
        self.toks: List[Tok] = toks
        self.i: int = 0

    #@ no_exception \all
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[self.i]


if __name__ == "__main__":
    assert Cur([Tok(7)]).cur().kind == 7
