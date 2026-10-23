r"""override strengthens requires, called via self in a base method"""
from typing import List
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.x = 0

    #@ requires v >= 0
    #@ ensures \result == v
    def f(self, v: int) -> int:
        return v

    def use(self, v: int) -> int:
        return self.f(v)


class B(A):
    #@ requires v >= 5
    #@ ensures \result == v
    def f(self, v: int) -> int:
        return 10 // (v - 4) * 0 + v


#@ ensures \result == 1
def probe() -> int:
    b = B()
    return b.use(4) - 3


if __name__ == "__main__":
    print("CPython:", probe())
