r"""Test 5891 -- driver run #3 route #226 polarity flip CONTROL (expected PASS): `[0] * 4` under `\length(self.disk) == 4` and `self.disk[0] == 0`; the goal states the fill `forall k. 0 <= k < 4 -> disk[k] = 0` and discharges; `ensures \result == 0` on `self.disk[0]` proves.
"""
# pycsl-expected: PASS
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 4
#@ class invariant self.disk[0] == 0
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [0] * 4

    #@ ensures \result == 0
    #@ assigns \nothing
    def first(self) -> int:
        return self.disk[0]


if __name__ == "__main__":
    print(D().first())
