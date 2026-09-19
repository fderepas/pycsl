from typing import List
_ = 0  # anchor


def g(a: List[int]) -> int:
    a[len(a):] = [1]
    return 0


#@ ensures \result == -1
def probe() -> int:
    xs: List[int] = []
    g(xs)
    return len(xs)
