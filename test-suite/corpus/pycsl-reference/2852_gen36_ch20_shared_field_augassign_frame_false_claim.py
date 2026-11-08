r"""Test 2852 — gen #36 ch20 (expected FAIL): FRAME. `self.n += 1` on a shared-field record
under `#@ assigns \nothing` is a write the contract does not declare; the store now goes
through the record's qualified label `a_n`, so Why3 must reject the unlisted write
(CPython: the field does change, 5 -> 6). The value claim is TRUE; only the frame lies.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class A:
    n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns \nothing
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
    assert a.n == 6
    b = B(5)
    b.drop()
    assert b.n == 2
