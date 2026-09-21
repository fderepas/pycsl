from typing import List


def g(m: List[List[int]]) -> int:
    m[0].append(1)
    return 0


#@ ensures \result == 0
def probe() -> int:
    m: List[List[int]] = [[]]
    _ = g(m)
    return len(m[0])
