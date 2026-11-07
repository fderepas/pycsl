r"""Test 5103 -- gen #37 route #226 increment 2c (expected FAIL): a PARAMLESS constructor storing the literal `[]` under `\length(self.xs) >= 1`, read across the module boundary. PROVED at base (no goal for a `\length` invariant); CPython `n(C())` is 0. 2c: `forall xs : array int. (Array.length xs) = 0 -> (Array.length xs >= 1)` FAILS.
"""
# pycsl-expected: FAIL

from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant \length(self.xs) >= 1
@mutable_state
class C:
    def __init__(self) -> None:
        self.xs: List[Tok] = []


#@ ensures \result >= 1
#@ assigns \nothing
def n(c: C) -> int:
    return len(c.xs)


if __name__ == "__main__":
    assert n(C()) == 0
