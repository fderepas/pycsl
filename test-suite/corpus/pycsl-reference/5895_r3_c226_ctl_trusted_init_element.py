r"""Test 5895 -- driver run #3 route #226 polarity flip CONTROL (expected PASS): a class whose `__init__` is `#@ \trusted` (the mirror parsers' shape): the establishment of its invariant is part of the declared TCB, so it is ADMITTED without a goal (not refused).
"""
# pycsl-expected: PASS
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.xs) >= 1
#@ class invariant self.xs[0] >= 0
@mutable_state
class D:
    #@ \trusted reviewer: pycsl-reference-5895
    #@ assigns \nothing
    def __init__(self, xs: List[int]) -> None:
        self.xs = xs

    #@ ensures \result >= 0
    #@ assigns \nothing
    def first(self) -> int:
        return self.xs[0]


if __name__ == "__main__":
    print(D([4]).first())
