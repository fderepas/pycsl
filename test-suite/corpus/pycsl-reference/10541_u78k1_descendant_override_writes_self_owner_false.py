r"""Test 10541 -- run #9 u78, review rt88 K1 (route #634), the OWNER of rt88's f23x: `R.total` is pure, the subclass `D(R)` overrides `total` and writes `self.a`, and `f(r: R)` declares `#@ assigns \nothing` and returns `r.total()`. No caller in this module: a caller in another module reads the declared frame and would assume its `D` argument unchanged. REFUSED (PYCSL-FUNCTION-FRAME; run9-u77 accepted it). `cd <tree root> && python <this file>` prints "CPython d.a after f(D(0)) = 5".
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


if __name__ == "__main__":
    d = D(0); f(d); print("CPython d.a after f(D(0)) =", d.a)
