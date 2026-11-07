r"""method with default arg used by instance"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 1

    def f(self, x: int = 3) -> int:
        return x + self.k


#@ ensures \result == 3
def probe() -> int:
    c = C()
    return c.f()


if __name__ == "__main__":
    print("CPython:", probe())
