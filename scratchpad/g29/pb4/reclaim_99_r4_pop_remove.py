from typing import List
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    xs.pop()
    return len(xs)
