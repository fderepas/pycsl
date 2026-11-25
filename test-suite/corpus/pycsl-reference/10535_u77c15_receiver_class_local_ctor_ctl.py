r"""Test 10535 -- run #9 u77, review rt87 c15 (PYCSL-FUNCTION-FRAME receiver-class narrowing, route #634). Control: the receiver is a LOCAL bound once to a constructor `q = R(r.a, r.b)`, so its class is R and the unrelated S.total is not charged. `cd <tree root> && python <this file>` prints "3 R(a=1, b=2)".
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class R:
    a: int
    b: int

    #@ ensures \result == self.a + self.b
    #@ assigns \nothing
    def total(self) -> int:
        return self.a + self.b


@dataclass
class S:
    n: int

    #@ ensures \result == 0
    #@ assigns self.n
    def total(self) -> int:
        self.n = self.n + 1
        return 0


#@ ensures \result == r.a + r.b
#@ assigns \nothing
def f(r: R) -> int:
    q = R(r.a, r.b)
    return q.total()


if __name__ == "__main__":
    r = R(1, 2); print(f(r), r)
