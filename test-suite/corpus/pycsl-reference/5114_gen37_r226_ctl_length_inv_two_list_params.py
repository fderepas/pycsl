r"""Test 5114 -- gen #37 route #226 increment 2c CONTROL (expected PASS): two list fields from two parameters (corpus 0933's shape), each with its own `#@ requires`; both premises are kept and the goal over both arrays PROVES. CPython `both(P([Tok(1)], [Tok(2)]))` is 2.
"""
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant \length(self.a) >= 1
#@ class invariant \length(self.b) >= 1
@mutable_state
class P:
    #@ requires len(a) >= 1
    #@ requires len(b) >= 1
    def __init__(self, a: List[Tok], b: List[Tok]) -> None:
        self.a: List[Tok] = a
        self.b: List[Tok] = b


#@ ensures \result >= 2
#@ assigns \nothing
def both(p: P) -> int:
    return len(p.a) + len(p.b)


if __name__ == "__main__":
    assert both(P([Tok(1)], [Tok(2)])) == 2
