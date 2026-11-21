r"""method keyword argument order"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def f(self, a: int, b: int) -> int:
        return a - b


#@ ensures \result == 1
def probe() -> int:
    c = C()
    return c.f(b=2, a=1)


if __name__ == "__main__":
    print("CPython:", probe())
