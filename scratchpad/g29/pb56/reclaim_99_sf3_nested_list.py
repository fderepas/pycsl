from typing import List
_ = 0  # anchor


def g(m: List[List[int]]) -> int:
    m[0].append(1)
    return 0


#@ ensures \result == 99
def probe() -> int:
    mm: List[List[int]] = [[]]
    g(mm)
    return len(mm[0])
