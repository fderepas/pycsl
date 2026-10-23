from typing import List
_ = 0  # anchor


def firstpos(xs: List[int]) -> int:
    for x in xs:
        if x > 0:
            return x
    return 0


#@ ensures \result == 1
def probe() -> int:
    ys: List[int] = [0, 5]
    return firstpos(ys)
