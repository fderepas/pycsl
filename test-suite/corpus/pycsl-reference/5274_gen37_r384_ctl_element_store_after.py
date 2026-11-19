r"""Test 5274 -- gen #37 route #384 (control, expected PASS): `[0] * 4` then the element store `self.disk[0] = 9` (length kept). PROVED.
"""
# pycsl-expected: PASS
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 4
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [0] * 4
        self.disk[0] = 9

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.disk[3]


if __name__ == "__main__":
    print(D().last())
