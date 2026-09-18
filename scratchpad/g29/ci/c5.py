r"""invariant broken via an aliased local"""
from typing import List
_ = 0  # anchor


#@ class invariant self.x >= 0
class A:
    def __init__(self) -> None:
        self.x = 0


def poke(a: A) -> None:
    a.x = -5


#@ ensures \result >= 0
def probe() -> int:
    a = A()
    poke(a)
    return a.x


if __name__ == "__main__":
    print("CPython:", probe())
