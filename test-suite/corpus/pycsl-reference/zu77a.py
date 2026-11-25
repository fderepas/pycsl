# u77 helper for witness 10537 (review rt87 c15, route #634): `f(r: R)` declares `assigns \nothing` and returns the pure `r.total()`; an unrelated class S has a self-writing `total`.
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
    n: int = 0

    #@ ensures \result == 0
    #@ assigns self.n
    def total(self) -> int:
        self.n = self.n + 1
        return 0


#@ ensures \result == r.a + r.b
#@ assigns \nothing
def f(r: R) -> int:
    return r.total()
