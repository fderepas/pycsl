r"""Test 5106 -- gen #37 route #226 increment 2c (expected FAIL): the token-cursor family (`self.i: int = 0` beside `self.toks = toks`) under `0 <= self.i < \length(self.toks)`, no `#@ requires`; `#@ no_exception \all` on `self.toks[self.i]` PROVED at base. CPython `Cur([]).cur()` raises IndexError. 2c: `forall toks : array int, i : int. toks = toks -> i = 0 -> ..` FAILS.
"""
# pycsl-expected: FAIL
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
@mutable_state
class Cur:
    def __init__(self, toks: List[int]) -> None:
        self.toks: List[int] = toks
        self.i: int = 0

    #@ no_exception \all
    #@ assigns \nothing
    def cur(self) -> int:
        return self.toks[self.i]


if __name__ == "__main__":
    try:
        Cur([]).cur()
        raise SystemExit("expected IndexError")
    except IndexError:
        print("IndexError")
