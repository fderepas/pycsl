from typing import List


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __str__(self) -> str:
        self.v = 7
        return 'c'


def k(o: C) -> int:
    return len(str(o))
