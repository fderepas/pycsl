r"""Test 1506 - ROUTE #150 (gen #29) control: `super().__init__(k + 100)` then `self.x = 3`; the subclass's own later store wins and `B(7).get() == 3` PROVES.
"""
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
        self.x = 3


#@ ensures \result == 3
#@ assigns \nothing
def probe() -> int:
    b = B(7)
    return b.get()

