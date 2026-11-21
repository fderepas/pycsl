r"""Test 1527 - ROUTE #155 (gen #29) positive twin of 1526: `C().get() == 7` PROVES (FAILS at HEAD).
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
    def __init__(self) -> None:
        super().__init__(7)


class C(B):
    def __init__(self) -> None:
        super().__init__()


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.get()

