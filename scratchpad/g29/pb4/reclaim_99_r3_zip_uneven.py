from typing import List
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    ys: List[int] = [10]
    n: int = 0
    for a, b in zip(xs, ys):
        n = n + 1
    return n
