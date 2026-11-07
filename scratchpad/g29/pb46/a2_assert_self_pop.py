from typing import List
_ = 0  # anchor


class Box:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2, 3]

    #@ ensures \result == 3
    def probe(self) -> int:
        assert self.xs.pop() == 3
        return len(self.xs)
