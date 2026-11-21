from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns \nothing
    def touch(self) -> int:
        self.n = 5
        return 0

    #@ ensures \result == 0
    def run(self) -> int:
        self.touch()
        return self.n
