r"""class constant list read as literal after instance mutation"""
from typing import List, Dict, Optional
_ = 0  # anchor


class C:
    XS: List[int] = [1]

    def __init__(self) -> None:
        self.k = 0

    def poke(self) -> None:
        C.XS[0] = 9


#@ ensures \result == 1
def probe() -> int:
    c = C()
    c.poke()
    return C.XS[0]


if __name__ == "__main__":
    print("CPython:", probe())
