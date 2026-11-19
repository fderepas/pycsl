r"""Test 2850 — gen #36 ch20 (expected PASS): two records share the field name `n`, so the
record declarations qualify it (`a_n`, `b_n`). `self.n += 1` / `self.n -= 3` must store
through the QUALIFIED label, exactly as `self.n = self.n + 1` does. At base the
augmented store wrote the bare `self.n` (unbound symbol, L3-tc failed — fail-closed); the
TRUE claims now prove (CPython agrees, see __main__).
"""
# pycsl-expected: PASS
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
