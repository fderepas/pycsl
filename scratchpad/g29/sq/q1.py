r"""sorted stability claim"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [3, 1, 2]
    ys = sorted(xs)
    return ys[2]


if __name__ == "__main__":
    print("CPython:", probe())
