r"""Test 10534 -- run #9 u77, review rt87 c15 (PYCSL-FUNCTION-FRAME receiver-class narrowing, route #634). R inherits `total` from its base B, and B.total writes `self.a`: the receiver family includes the ancestors, so `f(r: R)` declaring `#@ assigns \nothing` is REFUSED (PYCSL-FUNCTION-FRAME). `cd <tree root> && python <this file>` prints "0 R(a=2, b=2)".
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class B:
    a: int

    #@ ensures \result == 0
    #@ assigns self.a
    def total(self) -> int:
        self.a = self.a + 1
        return 0


@dataclass
class R(B):
    b: int


@dataclass
class S:
    n: int

    #@ ensures \result == self.n
    #@ assigns \nothing
    def total(self) -> int:
        return self.n


#@ ensures \result == 0
#@ assigns \nothing
def f(r: R) -> int:
    return r.total()


if __name__ == "__main__":
    r = R(1, 2); print(f(r), r)
