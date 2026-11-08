from typing import List
_ = 0  # anchor


class Alpha:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \result == 7
    def get(self) -> int:
        return 7


class Beta:
    def __init__(self) -> None:
        self.k = 0

    #@ requires self.k != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.k // self.k


#@ ensures \result == 7
def probe() -> int:
    o = Beta()
    return o.get()
