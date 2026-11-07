r"""Test 5880 -- driver run #3 route #226 polarity flip (expected FAIL): `[0] * 4` then an ELEMENT store `self.disk[0] = 1` under `self.disk[0] == 0`; the element term left no goal and `ensures \result == 0` on `self.disk[0]` PROVED (CPython 1). The contents after an element store are not modelled: REFUSED.
"""
# pycsl-expected: FAIL
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 4
#@ class invariant self.disk[0] == 0
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [0] * 4
        self.disk[0] = 1

    #@ ensures \result == 0
    #@ assigns \nothing
    def first(self) -> int:
        return self.disk[0]


if __name__ == "__main__":
    print(D().first())
