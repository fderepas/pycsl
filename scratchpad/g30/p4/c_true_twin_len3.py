from typing import List


#@ ensures \result == 3
def probe() -> int:
    xs: List[int] = sorted(x for x in [3, 1, 2])
    return len(xs)
