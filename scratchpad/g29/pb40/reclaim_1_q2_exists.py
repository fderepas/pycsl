from typing import List
_ = 0  # anchor


#@ ensures \exists i: int; 0 <= i and i < 2 and xs[i] == 9
def g(xs: List[int]) -> int:
    return 0


#@ ensures \result == 1
def probe() -> int:
    ys: List[int] = [1, 2]
    return g(ys)
