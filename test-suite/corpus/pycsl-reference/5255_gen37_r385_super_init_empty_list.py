r"""Test 5255 -- gen #37 route #385 (expected FAIL): `super().__init__([])` into `#@ requires len(toks) >= 1`: unchecked; now REFUSED (PYCSL-R385-DELEGATED-INIT-REQUIRES-UNCHECKED; CPython IndexError). PROVED at base 0a2d8019b.
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

    #@ no_exception \all
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[0]


@mutable_state
class Sub(Cur):
    def __init__(self) -> None:
        super().__init__([])


if __name__ == "__main__":
    try:
        Sub().cur()
        print("no violation")
    except IndexError as e:
        print("VIOLATION IndexError", e)
