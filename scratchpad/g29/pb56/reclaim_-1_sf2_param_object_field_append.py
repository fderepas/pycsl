from typing import List
_ = 0  # anchor


class Box:
    def __init__(self) -> None:
        self.xs: List[int] = []


def g(box: Box) -> int:
    box.xs.append(1)
    return 0


#@ ensures \result == -1
def probe() -> int:
    b = Box()
    g(b)
    return len(b.xs)
