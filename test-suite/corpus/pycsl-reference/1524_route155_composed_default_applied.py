r"""Test 1524 - ROUTE #155 (gen #29) positive twin of 1522: `B().get() == 5` PROVES (FAILS at HEAD).
"""
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


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    b = B()
    return b.get()

