r"""Test 10536 -- run #9 u77, review rt87 c15 (PYCSL-FUNCTION-FRAME receiver-class narrowing, route #634). The receiver `q` is bound to `r` and conditionally rebound to `s: S` (whose total writes `self.n`): not a constructor-bound local, so the conservative any-class rule applies and `f` declaring `#@ assigns \nothing` is REFUSED (PYCSL-FUNCTION-FRAME, "`r`, `s`"). `cd <tree root> && python <this file>` prints "0 R(a=1, b=2) S(n=1)": s is written.
"""
# pycsl-expected: FAIL
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


#@ ensures \result == 0
#@ assigns \nothing
def f(r: R, s: S) -> int:
    q = r
    if r.a > 0:
        q = s
    return q.total()


if __name__ == "__main__":
    r = R(1, 2); s = S(0); print(f(r, s), r, s)
