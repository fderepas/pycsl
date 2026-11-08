from typing import List
_ = 0  # anchor


def bump(zs: List[int]) -> int:
    zs[0] = zs[0] + 1
    return 0


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [1]
    assert bump(xs) == 0
    return xs[0]
