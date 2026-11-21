r"""override weakens ensures used by base method"""
from typing import List
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.x = 0

    #@ ensures \result >= 0
    def f(self) -> int:
        return 1

    #@ ensures \result >= 0
    def use(self) -> int:
        return self.f()


class B(A):
    def f(self) -> int:
        return -5


#@ ensures \result >= 0
def probe() -> int:
    b = B()
    return b.use()


if __name__ == "__main__":
    print("CPython:", probe())
