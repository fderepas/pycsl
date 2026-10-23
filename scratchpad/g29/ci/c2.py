r"""invariant broken through a list of instances"""
from typing import List
_ = 0  # anchor


#@ class invariant self.x >= 0
class A:
    def __init__(self) -> None:
        self.x = 0


#@ ensures \result >= 0
def probe() -> int:
    xs: List[A] = [A()]
    xs[0].x = -3
    return xs[0].x


if __name__ == "__main__":
    print("CPython:", probe())
