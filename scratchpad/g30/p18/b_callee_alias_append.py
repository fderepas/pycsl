from typing import List


def g(a: List[int]) -> int:
    b = a
    b.append(1)
    return 0


#@ ensures \result == 0
def probe() -> int:
    a: List[int] = []
    _ = g(a)
    return len(a)
