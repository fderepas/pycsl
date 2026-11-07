r"""invariant broken via setattr"""
from typing import List
_ = 0  # anchor


#@ class invariant self.x >= 0
class A:
    def __init__(self) -> None:
        self.x = 0


#@ ensures \result >= 0
def probe() -> int:
    a = A()
    setattr(a, "x", -4)
    return a.x


if __name__ == "__main__":
    print("CPython:", probe())
