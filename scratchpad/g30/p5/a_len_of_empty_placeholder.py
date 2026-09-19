from typing import List


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    return len(xs)
