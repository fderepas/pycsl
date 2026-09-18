r"""module constant list mutated by a helper called at module scope"""
from typing import List, Dict
_ = 0  # anchor


XS: List[int] = [1]


def poke() -> None:
    XS[0] = 9


poke()


#@ ensures \result == 1
def probe() -> int:
    return XS[0]


if __name__ == "__main__":
    print("CPython:", probe())
