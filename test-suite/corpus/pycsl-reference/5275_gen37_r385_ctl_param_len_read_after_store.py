r"""Test 5275 -- gen #37 route #385 (control, expected PASS): a list field bound to its `__init__` parameter, with `len(toks)` read after the store (`self.n = len(toks)`) and `#@ requires len(toks) >= 1`. PROVED.
"""
# pycsl-expected: PASS
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
        self.n: int = len(toks)

    #@ no_exception \all
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[0]


if __name__ == "__main__":
    print(Cur([Tok(7)]).cur())
