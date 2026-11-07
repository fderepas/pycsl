from typing import Set

class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.n
    def __init__(self) -> None:
        self.n: int = 0

    #@ requires 1 not in s
    #@ ensures 1 not in s
    #@ assigns \nothing
    def m(self, s: Set[int]) -> None:
        s.add(1)
