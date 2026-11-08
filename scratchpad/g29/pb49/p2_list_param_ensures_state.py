from typing import List
_ = 0  # anchor


#@ ensures \result == xs[0] - 99
def f(xs: List[int]) -> int:
    xs[0] = 99
    return 0


#@ ensures \result == 0 - 94
def probe() -> int:
    ys: List[int] = [5]
    return f(ys)
