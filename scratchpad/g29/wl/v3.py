r"""mutating helper call inside comprehension"""
from typing import List, Dict
_ = 0  # anchor


def poke(xs: List[int]) -> int:
    xs[0] = 7
    return 0


#@ ensures \result == 0
def probe() -> int:
    ys: List[int] = [0]
    zs = [poke(ys) for x in [1]]
    return ys[0]


if __name__ == "__main__":
    print("CPython:", probe())
