r"""Test 10532 -- run #9 u77, review rt87 c15 (PYCSL-FUNCTION-FRAME receiver-class narrowing, route #634). Control: `f(r: R)` with `#@ assigns \nothing` returns `r.total()`; `R.total` is pure, and an UNRELATED class S has a `total` that writes `self.n`. The dotted call is resolved through the parameter annotation `R` (its class family: R, ancestors, descendants), so S.total is not charged to `r`. `cd <tree root> && python <this file>` prints "3 R(a=1, b=2)". run9-u76 REFUSED it (PYCSL-FUNCTION-FRAME, "may write `r`"); L21 proved it.
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


if __name__ == "__main__":
    r = R(1, 2); print(f(r), r)
