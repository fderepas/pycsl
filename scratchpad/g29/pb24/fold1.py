from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2]
    if any(x > 1 for x in xs):
        return 1
    return 0
