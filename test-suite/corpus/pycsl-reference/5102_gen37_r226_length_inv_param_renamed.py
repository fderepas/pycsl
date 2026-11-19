r"""Test 5102 -- gen #37 route #226 increment 2c (expected FAIL): the list field is bound to a parameter of a DIFFERENT name (`self.toks = tokens`), invariant `\length(self.toks) >= 2`, no `#@ requires`. PROVED at base (`ensures \result >= 2`); CPython `n(P([Tok(1)]))` is 1. 2c: `forall toks tokens : array int. toks = tokens -> ..` FAILS.
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
    def __init__(self, tokens: List[Tok]) -> None:
        self.toks: List[Tok] = tokens


#@ ensures \result >= 2
#@ assigns \nothing
def n(p: P) -> int:
    return len(p.toks)


if __name__ == "__main__":
    assert n(P([Tok(1)])) == 1
