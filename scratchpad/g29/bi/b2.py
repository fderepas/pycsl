r"""reversed list first"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    ys = list(reversed(xs))
    return ys[0]


if __name__ == "__main__":
    print("CPython:", probe())
