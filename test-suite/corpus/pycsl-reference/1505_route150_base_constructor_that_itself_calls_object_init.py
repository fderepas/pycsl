r"""Test 1505 - ROUTE #150 (gen #29) control: the base `A.__init__` itself starts with `super().__init__()` (object's no-op); composing `B`'s `super().__init__(k + 100)` over it still PROVES `B(7).get() == 107` (FAILS at HEAD).
"""
_ = 0  # anchor


class A:
    def __init__(self, k: int) -> None:
        super().__init__()
        self.x = k

    #@ requires True
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


class B(A):
    def __init__(self, k: int) -> None:
        super().__init__(k + 100)


#@ ensures \result == 107
#@ assigns \nothing
def probe() -> int:
    b = B(7)
    return b.get()

