from typing import List
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    ys: List[int] = [x + 1 for x in xs]
    return len(ys)
