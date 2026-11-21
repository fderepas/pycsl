from typing import List


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1


#@ ensures \result >= 0 or \result < 0
def k(o: C) -> int:
    return len(o)
