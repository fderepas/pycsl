from typing import List
_ = 0  # anchor


class Box:
    def __init__(self, xs: List[int]) -> None:
        self.xs = xs


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [1, 2]
    b = Box(xs)
    b.xs[0] = 9
    return xs[0]
