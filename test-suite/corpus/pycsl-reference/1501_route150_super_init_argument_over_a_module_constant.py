r"""Test 1501 - ROUTE #150 (gen #29): `super().__init__(K)` with `K = 50` a module constant; the composed value is not over this constructor's parameters, so the field is UNKNOWN. `B().get() == 0` PROVED at HEAD; CPython 50.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
K = 50


class A:
    def __init__(self, k: int) -> None:
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self) -> None:
        super().__init__(K)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    b = B()
    return b.get()

