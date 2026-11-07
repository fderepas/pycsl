r"""Test 5247 -- gen #37 route #385 (expected FAIL): `[0] * 4` then `self.disk, self.k = [], 0` under `\length == 4`: the goal read the first store; now REFUSED (R384; CPython IndexError). PROVED at base 0a2d8019b.
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
        self.disk, self.k = [], 0

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
