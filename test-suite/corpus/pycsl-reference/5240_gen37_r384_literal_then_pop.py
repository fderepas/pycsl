r"""Test 5240 -- gen #37 route #384 (expected FAIL): `self.disk = [0] * 4; self.disk.pop()` under `\length(self.disk) == 4`: no goal, invariant assumed; now the goal binds the END length (`length = 3 -> length = 4`) and FAILS (CPython IndexError on `self.disk[3]`). PROVED at base 0a2d8019b.
"""
# pycsl-expected: FAIL
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 4
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
