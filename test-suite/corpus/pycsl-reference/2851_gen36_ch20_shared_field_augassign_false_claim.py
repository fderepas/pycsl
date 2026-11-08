r"""Test 2851 — gen #36 ch20 (expected FAIL): FALSE twin of 2850. Same shared-field records;
`self.n += 1` does NOT add 2 (CPython: 5 -> 6), so `self.n == \old(self.n) + 2` must stay
UNPROVED now that the augmented store type-checks (non-vacuity of the repair).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class A:
    n: int = 0

    #@ ensures self.n == \old(self.n) + 2
    #@ assigns self.n
    def bump(self) -> None:
        self.n += 1


@dataclass
class B:
    n: int = 0

    #@ ensures self.n == \old(self.n) - 3
    #@ assigns self.n
    def drop(self) -> None:
        self.n -= 3


if __name__ == "__main__":
    a = A(5)
    a.bump()
    assert a.n == 6 and a.n != 5 + 2
    b = B(5)
    b.drop()
    assert b.n == 2
