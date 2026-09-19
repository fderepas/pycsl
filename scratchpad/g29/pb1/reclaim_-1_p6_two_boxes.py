from typing import List
_ = 0  # anchor


class Box:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]


#@ ensures \result == -1
def probe() -> int:
    a = Box()
    b = a
    b.xs[0] = 9
    return a.xs[0]
