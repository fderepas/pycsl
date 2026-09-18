r"""recursive method"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    #@ requires n >= 0
    #@ ensures \result == 0
    def f(self, n: int) -> int:
        if n == 0:
            return 0
        return self.f(n - 1) + 1


#@ ensures \result == 0
def probe() -> int:
    return C().f(2)


if __name__ == "__main__":
    print("CPython:", probe())
