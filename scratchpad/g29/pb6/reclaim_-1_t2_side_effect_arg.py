from typing import List
_ = 0  # anchor


def add1(x: int) -> int:
    return x + 1


#@ ensures \result == -1
def probe() -> int:
    xs: List[int] = [1, 2]
    return add1(add1(xs[0])) + add1(xs[1])
