r"""method stored field then called unbound"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        self.k = k

    def f(self) -> int:
        return self.k


#@ ensures \result == 0
def probe() -> int:
    c = C(4)
    return C.f(c)


if __name__ == "__main__":
    print("CPython:", probe())
