r"""Test 1522 - ROUTE #155 (gen #29, carrier of its own landed #150): `B.__init__(self): super().__init__()` over `A.__init__(self, k: int = 5)`; the composed entry `x = 5` was never applied because B has no parameters, `{ b_x = 0 }` and `B().get() == 0` PROVED; CPython 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class A:
    def __init__(self, k: int = 5) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self) -> None:
        super().__init__()


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    b = B()
    return b.get()

