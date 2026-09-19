from typing import List
_ = 0  # anchor


class Box:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2, 3]


_b = Box()


#@ ensures \result == 3
def probe() -> int:
    assert _b.xs.pop() == 3
    return len(_b.xs)
