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


class Mid:
    def __init__(self) -> None:
        self.leaf = Beta()


class Top:
    def __init__(self) -> None:
        self.mid = Mid()

    #@ ensures \result == 1
    def run(self) -> int:
        return self.mid.leaf.get()
