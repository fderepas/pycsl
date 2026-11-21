from typing import List
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    xs: List[int] = [1, 2]
    ys: List[int] = [10, 20]
    s: int = 0
    for a, b in zip(xs, ys):
        s = s + a * b
    return s
