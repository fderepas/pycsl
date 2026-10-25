r"""Test 5112 -- gen #37 route #226 increment 2c CONTROL (expected PASS): 5104 with the TRUE length, `self.disk = [Tok(0)] * 4` under `\length(self.disk) == 4`. `(Array.length disk) = 4 -> ((Array.length disk) = 4)` PROVES. CPython `n(C())` is 4.
"""
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant \length(self.disk) == 4
@mutable_state
class C:
    def __init__(self) -> None:
        self.disk: List[Tok] = [Tok(0)] * 4


#@ ensures \result == 4
#@ assigns \nothing
def n(c: C) -> int:
    return len(c.disk)


if __name__ == "__main__":
    assert n(C()) == 4
