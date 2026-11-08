r"""Test 3935 -- gen #37 route #308 (expected FAIL): `self.ys[self.nxt()] += 1` in a method: the index method ran twice; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import List

class K:
    def __init__(self) -> None:
        self.ys: List[int] = [0, 0, 0, 0]
        self.c: int = 0

    #@ assigns self.c
    #@ ensures \result == \old(self.c) + 1 and self.c == \old(self.c) + 1
    def nxt(self) -> int:
        self.c = self.c + 1
        return self.c

    #@ requires self.c == 0 and len(self.ys) == 4
    #@ ensures \result == 2
    def f(self) -> int:
        self.ys[self.nxt()] += 1
        return self.c

if __name__ == "__main__":
    assert K().f() == 2
