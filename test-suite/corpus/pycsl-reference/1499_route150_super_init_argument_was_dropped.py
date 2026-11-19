r"""Test 1499 - ROUTE #150 (gen #29): `B.__init__: super().__init__(k + 100)` over `A.__init__: self.x = k`; the base field kept its witness (`{ b_x = 0 }`) and `B(7).get() == 0` PROVED; CPython 107. A LEADING `super().__init__(<args>)` is now COMPOSED faithfully.
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


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    b = B(7)
    return b.get()

