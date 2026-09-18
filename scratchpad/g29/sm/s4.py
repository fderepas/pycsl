r"""overridden method via base-typed parameter"""
from typing import List
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.k = 0

    def f(self) -> int:
        return 1


class B(A):
    def f(self) -> int:
        return 2


def use(a: A) -> int:
    return a.f()


#@ ensures \result == 1
def probe() -> int:
    return use(B())


if __name__ == "__main__":
    print("CPython:", probe())
