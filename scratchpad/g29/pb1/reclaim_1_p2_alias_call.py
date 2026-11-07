from typing import List
_ = 0  # anchor


def bump(zs: List[int]) -> int:
    zs[0] = zs[0] + 1
    return 0


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2]
    bump(xs)
    return xs[0]
