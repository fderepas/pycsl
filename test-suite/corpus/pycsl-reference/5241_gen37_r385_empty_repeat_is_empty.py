r"""Test 5241 -- gen #37 route #385 (expected FAIL): `[] * 4` under `\length(self.disk) == 4`: the goal read length 4; `[] * N` is EMPTY, now `length = 0 -> length = 4` FAILS (CPython IndexError). PROVED at base 0a2d8019b.
"""
# pycsl-expected: FAIL
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) == 4
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = [] * 4

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
