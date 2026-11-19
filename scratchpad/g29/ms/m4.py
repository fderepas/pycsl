r"""method mutating self via alias list stored in field"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [0]

    #@ assigns \nothing
    def m(self) -> None:
        ys = self.xs
        ys[0] = 9


#@ ensures \result == 0
def probe() -> int:
    c = C()
    c.m()
    return c.xs[0]


if __name__ == "__main__":
    print("CPython:", probe())
