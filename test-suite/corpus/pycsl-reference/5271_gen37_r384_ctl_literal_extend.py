r"""Test 5271 -- gen #37 route #384 (control, expected PASS): `[0, 0]` then `extend([0, 0])`: end length 4. PROVED.
"""
# pycsl-expected: PASS
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 4
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [0, 0]
        self.disk.extend([0, 0])

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.disk[3]


if __name__ == "__main__":
    print(D().last())
