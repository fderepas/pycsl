r"""Test 1526 - ROUTE #155 (gen #29): `C.__init__(): super().__init__()` over `B.__init__(): super().__init__(7)` over `A.__init__(k)`; `{ c_x = 0 }` and `C().get() == 0` PROVED at HEAD; CPython 7.
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
    def __init__(self) -> None:
        super().__init__(7)


class C(B):
    def __init__(self) -> None:
        super().__init__()


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.get()

