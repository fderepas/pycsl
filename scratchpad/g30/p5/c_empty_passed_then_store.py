from typing import List


def seed(ys: List[int]) -> int:
    return len(ys)


#@ no_exception IndexError
#@ ensures \result == 5
def probe() -> int:
    xs: List[int] = []
    _ = seed(xs)
    xs[0] = 5
    return xs[0]
