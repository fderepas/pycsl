r"""Test 5893 -- driver run #3 route #226 polarity flip CONTROL (expected PASS): the 0663 shape — `[0] * 16` under a quantified byte-range invariant; the fill premise discharges it.
"""
# pycsl-expected: PASS
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 16
#@ class invariant \forall i; 0 <= i and i < 16 ==> (0 <= self.disk[i] and self.disk[i] <= 255)
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [0] * 16

    #@ requires 0 <= pos and pos < 16
    #@ ensures 0 <= \result and \result <= 255
    #@ assigns \nothing
    def byte(self, pos: int) -> int:
        return self.disk[pos]


if __name__ == "__main__":
    print(D().byte(3))
