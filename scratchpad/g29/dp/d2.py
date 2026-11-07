r"""same-name method in two classes, one guarded"""
from typing import List, Dict, Optional
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.x = 0

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


class B:
    def __init__(self) -> None:
        self.x = 5

    #@ ensures \result == 2
    def get(self) -> int:
        return 2


#@ ensures \result == 7
def probe() -> int:
    b = B()
    return b.get() + 5


if __name__ == "__main__":
    print("CPython:", probe())
