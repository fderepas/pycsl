r"""Test 3693 -- gen #37 ch33 (expected FAIL): false twin of 3692: `\result == self.toks[1]` for a body returning `self.toks[0]` must NOT prove.
"""
# pycsl-expected: FAIL
from typing import List


#@ class invariant \length(self.toks) >= 0
class P:
    def __init__(self) -> None:
        self.toks: List[int] = [1, 2, 3]
        self.i: int = 0

    #@ requires \length(self.toks) >= 1
    #@ ensures \result == self.toks[1]
    #@ assigns \nothing
    def first(self) -> int:
        return self.toks[0]


class Q:
    def __init__(self) -> None:
        self.toks: List[int] = [7]
