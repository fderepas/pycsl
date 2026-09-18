r"""invariant broken in constructor argument"""
from typing import List
_ = 0  # anchor


#@ class invariant self.x >= 0
class A:
    def __init__(self, v: int) -> None:
        self.x = v


#@ ensures \result >= 0
def probe() -> int:
    a = A(-2)
    return a.x


if __name__ == "__main__":
    print("CPython:", probe())
