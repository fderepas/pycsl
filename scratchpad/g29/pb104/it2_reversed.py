from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    s: int = 0
    for x in reversed(xs):
        s = s * 10 + x
    return s
