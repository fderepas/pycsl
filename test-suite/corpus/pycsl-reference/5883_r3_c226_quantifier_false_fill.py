r"""Test 5883 -- driver run #3 route #226 polarity flip (expected FAIL): `[-1] * 4` under `\forall i; 0 <= i < 4 ==> self.disk[i] >= 0`; the quantifier left no goal and `ensures \result >= 0` on `self.disk[2]` PROVED (CPython -1). Now stated with the fill premise `disk[k] = (-1)`, which FAILS.
"""
# pycsl-expected: FAIL
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 4
#@ class invariant \forall i; 0 <= i and i < 4 ==> self.disk[i] >= 0
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [-1] * 4

    #@ ensures \result >= 0
    #@ assigns \nothing
    def third(self) -> int:
        return self.disk[2]


if __name__ == "__main__":
    print(D().third())
