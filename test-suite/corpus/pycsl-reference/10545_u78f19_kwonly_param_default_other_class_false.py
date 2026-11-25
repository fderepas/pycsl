r"""Test 10545 -- run #9 u78, review rt88 f19 (route #634), the KEYWORD-ONLY form: `f(t: T, *, r: R = S(0))` declares `#@ assigns \nothing` and returns `r.total(t)`; the default is an `S`, whose `total` writes `t.v` (a non-literal keyword-only default is not even recorded in `param_defaults`). A keyword-only parameter is not narrowed: REFUSED (PYCSL-FUNCTION-FRAME, `t`). `cd <tree root> && python <this file>` prints "CPython f(T(0)) = 0 , t.v = 1".
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class T:
    v: int = 0


@dataclass
class R:
    a: int = 0

    #@ ensures \result == self.a
    #@ assigns \nothing
    def total(self, t: T) -> int:
        return self.a


@dataclass
class S:
    n: int = 0

    #@ ensures \result == 0
    #@ assigns t.v
    def total(self, t: T) -> int:
        t.v = t.v + 1
        return 0


#@ assigns \nothing
def f(t: T, *, r: R = S(0)) -> int:
    return r.total(t)


if __name__ == "__main__":
    t = T(0); print("CPython f(T(0)) =", f(t), ", t.v =", t.v)
