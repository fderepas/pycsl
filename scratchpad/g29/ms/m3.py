r"""method mutating another instance's field"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    #@ assigns \nothing
    def m(self, o: "C") -> None:
        o.k = 9


#@ ensures \result == 0
def probe() -> int:
    a = C()
    b = C()
    a.m(b)
    return b.k


if __name__ == "__main__":
    print("CPython:", probe())
