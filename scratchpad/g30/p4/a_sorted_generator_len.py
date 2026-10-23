from typing import List


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = sorted(x for x in [3, 1, 2])
    return len(xs)
