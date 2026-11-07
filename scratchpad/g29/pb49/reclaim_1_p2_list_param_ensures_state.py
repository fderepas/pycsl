from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    xs[0] = 99
    return 0


#@ ensures \result == 1
def probe() -> int:
    ys: List[int] = [5]
    return f(ys)
