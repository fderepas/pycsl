r"""Test 10540 -- run #9 u78, review rt88 K1 (PYCSL-FUNCTION-FRAME receiver-class narrowing, route #634). `R.total` is pure; the SUBCLASS `D(R)` overrides `total` and writes `self.a` (a SELF write, not a parameter position, so PYCSL-OVERRIDE-FRAME is silent). `f(r: R)` declaring `#@ assigns \nothing` returns `r.total()`: a `D` reaches `r`, so `f` may write `r`. REFUSED (PYCSL-FUNCTION-FRAME): an override of `total` exists, so the receiver class is not narrowed. `cd <tree root> && python <this file>` prints "CPython g() = 5 , claim 0".
"""
# pycsl-expected: FAIL


class R:
    def __init__(self, a: int = 0) -> None:
        self.a = a

    #@ ensures \result == self.a
    def total(self) -> int:
        return self.a


class D(R):
    def __init__(self, a: int = 0) -> None:
        self.a = a

    #@ ensures \result == 0
    def total(self) -> int:
        self.a = 5
        return 0


#@ assigns \nothing
def f(r: R) -> int:
    return r.total()


#@ ensures \result == 0
def g() -> int:
    d = D(0)
    f(d)
    return d.a


if __name__ == "__main__":
    print("CPython g() =", g(), ", claim 0")
