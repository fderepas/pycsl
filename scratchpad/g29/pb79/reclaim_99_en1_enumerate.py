from typing import List
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [10, 20]
    s: int = 0
    for i, v in enumerate(xs):
        s = s + i * v
    return s
