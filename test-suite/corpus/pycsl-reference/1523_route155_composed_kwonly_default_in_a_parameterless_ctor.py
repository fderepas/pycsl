r"""Test 1523 - ROUTE #155 (gen #29): the keyword-only twin (`*, k: int = 5`); `B().get() == 0` PROVED; CPython 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class A:
    def __init__(self, *, k: int = 5) -> None:
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

