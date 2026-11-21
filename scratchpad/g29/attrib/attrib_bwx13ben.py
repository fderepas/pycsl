from typing import List
_ = 0  # anchor


class Alpha:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \result == 1
    def get(self) -> int:
        return 1


class Beta:
    def __init__(self) -> None:
        self.k = 2

    #@ ensures \result == 2
    def get(self) -> int:
        return 2


class Outer:
    def __init__(self) -> None:
        self.inner = Beta()

    #@ ensures \result == 1
    def run(self) -> int:
        return self.inner.get()
