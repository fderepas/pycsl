from typing import List


#@ ensures \result == 3
def probe() -> int:
    ys: List[int] = [3, 1, 2]
    xs: List[int] = sorted(ys)
    return len(xs)
