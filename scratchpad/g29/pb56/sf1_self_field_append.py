from typing import List
_ = 0  # anchor


class Box:
    def __init__(self) -> None:
        self.xs: List[int] = []

    #@ assigns self.xs
    def add(self) -> int:
        self.xs.append(1)
        return 0


#@ ensures \result == 0
def probe() -> int:
    b = Box()
    b.add()
    return len(b.xs)
