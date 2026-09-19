from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe(flag: int) -> int:
    xs: List[int] = [1]
    if flag > 0:
        xs = [1, 2, 3]
    return len(xs)
