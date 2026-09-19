from typing import List
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    return xs[-1]
