from typing import List
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    a: List[int] = [1, 2]
    b: List[int] = [1, 2]
    if a == b:
        return 1
    return 0
