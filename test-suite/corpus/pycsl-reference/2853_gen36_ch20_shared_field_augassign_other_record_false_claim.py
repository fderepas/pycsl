r"""Test 2853 — gen #36 ch20 (expected FAIL): the augmented store must hit THIS record's
label, not the other record's. `B.bump_b` does `self.n += 10` and claims `A`'s field-sized
step `self.n == \old(self.n) + 1` — FALSE (CPython: 5 -> 15). A store routed to the wrong
label could not even type-check (distinct record types); this pins the value as well.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class A:
    n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def bump(self) -> None:
        self.n += 1


@dataclass
class B:
    n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def bump_b(self) -> None:
        self.n += 10


if __name__ == "__main__":
    a = A(5)
    a.bump()
    assert a.n == 6
    b = B(5)
    b.bump_b()
    assert b.n == 15 and b.n != 5 + 1
