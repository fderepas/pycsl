from typing import List
_ = 0  # anchor


class Box:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2, 3]


_b = Box()


#@ ensures \result == 0
def probe() -> int:
    ys: List[int] = [0]
    ys[0] = 1
    assert _b.xs.pop() == 3
    return len(_b.xs) + ys[0] - 1
