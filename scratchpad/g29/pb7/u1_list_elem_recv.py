from typing import List
_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.k = 0

    #@ raises ValueError when v < 0
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


class Outer:
    def __init__(self) -> None:
        self.boxes: List[Inner] = [Inner()]

    #@ no_exception ValueError
    #@ ensures \result == 0
    def run(self) -> int:
        self.boxes[0].go(-1)
        return 0
