r"""guarded method through a returned receiver"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


def make() -> C:
    return C(0)


#@ ensures \result == 5
def probe() -> int:
    make().get()
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
