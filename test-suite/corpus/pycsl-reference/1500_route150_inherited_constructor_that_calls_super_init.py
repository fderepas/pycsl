r"""Test 1500 - ROUTE #150 x #147 (gen #29): `C(B)` inherits `B.__init__`, which calls `super().__init__(k + 100)`; `C(7).get() == 0` PROVED; CPython 107.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class A:
    def __init__(self, k: int) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self, k: int) -> None:
        super().__init__(k + 100)
        self.y = 1


class C(B):
    pass


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(7)
    return c.get()

