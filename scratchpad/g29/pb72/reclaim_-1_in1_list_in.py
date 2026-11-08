from typing import List
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    xs: List[int] = [1, 2]
    if 5 in xs:
        return 1
    return 0
