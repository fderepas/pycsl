r"""Test 10544 -- run #9 u78, review rt88 K1 (route #634), a GRANDCHILD override: `R.total` is pure, `D(R)` does not define `total`, and `E(D)` overrides it and writes `self.a`. `f(r: R)` declares `#@ assigns \nothing` and returns `r.total()`. REFUSED (PYCSL-FUNCTION-FRAME): route #278's MRO pair (e__total, r__total) disables the narrowing. `cd <tree root> && python <this file>` prints "CPython e.a after f(E(0)) = 5".
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


class E(D):
    def __init__(self, a: int = 0) -> None:
        self.a = a

    #@ ensures \result == 0
    def total(self) -> int:
        self.a = 5
        return 0


#@ assigns \nothing
def f(r: R) -> int:
    return r.total()


if __name__ == "__main__":
    e = E(0); f(e); print("CPython e.a after f(E(0)) =", e.a)
