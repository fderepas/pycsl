r"""zip truncation length"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    ys: List[int] = [4, 5]
    n = 0
    for a, b in zip(xs, ys):
        n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
