from typing import List
_ = 0  # anchor


class Alpha:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \result == 0
    def go(self, v: int) -> int:
        return 0


class Beta:
    def __init__(self) -> None:
        self.k = 2

    #@ raises ValueError when v < 0
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    o = Beta()
    return o.go(0 - 1)
