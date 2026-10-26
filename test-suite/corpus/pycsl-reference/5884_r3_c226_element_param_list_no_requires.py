r"""Test 5884 -- driver run #3 route #226 polarity flip (expected FAIL): a list PARAMETER field under `self.xs[0] >= 0` with no `#@ requires` on `__init__`; the element term left no goal and `ensures \result >= 0` on `self.xs[0]` PROVED (CPython -5). Now stated `forall xs : array int. xs = xs -> ..`, which FAILS.
"""
# pycsl-expected: FAIL
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.xs) == 1
#@ class invariant self.xs[0] >= 0
@mutable_state
class D:
    def __init__(self, xs: List[int]) -> None:
        self.xs = xs

    #@ ensures \result >= 0
    #@ assigns \nothing
    def first(self) -> int:
        return self.xs[0]


if __name__ == "__main__":
    print(D([-5]).first())
