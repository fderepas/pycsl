r"""Test 5273 -- gen #37 route #384 (control, expected PASS): `bytearray(N)` with a module constant `N = 6` bound once, under `\length == 6`. PROVED.
"""
# pycsl-expected: PASS
from typing import List


def mutable_state(cls):
    return cls


N = 6


#@ class invariant \length(self.disk) == 6
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: list = bytearray(N)

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.disk[5]


if __name__ == "__main__":
    print(D().last())
