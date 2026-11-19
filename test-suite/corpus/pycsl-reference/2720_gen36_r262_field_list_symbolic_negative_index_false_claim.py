r"""Test 2720 — route #262 (expected FAIL): `self.<list field>[k]` in a method contract took
the field-array arm, which never normalised an index, so with `k == -1` the raw cell `-1`
was framed across `self.items[1] = 7` and PROVED at b35d9c5e. CPython: items[-1] 0 -> 7.
"""
# pycsl-expected: FAIL
from typing import List


class Box:
    def __init__(self) -> None:
        self.items: List[int] = [0, 0]

    #@ requires \length(self.items) == 2 and k == -1
    #@ requires self.items[1] == 0
    #@ ensures self.items[k] == \old(self.items[k])
    #@ assigns self.items[1]
    def poke(self, k: int) -> None:
        self.items[1] = 7


if __name__ == "__main__":
    b = Box()
    b.poke(-1)
    assert b.items[-1] == 7
