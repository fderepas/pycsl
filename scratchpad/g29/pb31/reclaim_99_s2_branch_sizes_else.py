from typing import List
_ = 0  # anchor


#@ ensures \result == 99
def probe(flag: int) -> int:
    if flag > 0:
        xs: List[int] = [1, 2, 3]
    else:
        xs: List[int] = [1]
    return len(xs)
