r"""Test 5242 -- gen #37 route #384 (expected FAIL): `[0] * -1` under `\length == 3`: no goal; a negative repeat is EMPTY, now `length = 0 -> ..` FAILS (CPython IndexError). PROVED at base 0a2d8019b.
"""
# pycsl-expected: FAIL
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 3
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [0] * -1

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.disk[2]


if __name__ == "__main__":
    try:
        D().last()
        print("no violation")
    except IndexError as e:
        print("VIOLATION IndexError", e)
