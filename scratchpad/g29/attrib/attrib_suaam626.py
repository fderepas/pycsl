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


class Outer:
    def __init__(self) -> None:
        self.inner = Beta()

    #@ no_exception ValueError
    #@ ensures \result == 0
    def run(self) -> int:
        return self.inner.go(0 - 1)
