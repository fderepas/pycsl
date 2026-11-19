r"""Test 5879 -- driver run #3 route #226 polarity flip (expected FAIL): the registered carrier `route384-carrier-element-term-masks-length-state.py`. `[0] * 4; self.disk.pop()` under `\length(self.disk) == 4` and `self.disk[0] == 0`: the element term stopped the goal before the length state was read, so the class was neither stated nor refused and `no_exception` on `self.disk[3]` PROVED (CPython IndexError). Now REFUSED.
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
        self.disk.pop()

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.disk[3]


if __name__ == "__main__":
    try:
        D().last()
        print("no violation")
    except IndexError as e:
        print("VIOLATION IndexError", e)
