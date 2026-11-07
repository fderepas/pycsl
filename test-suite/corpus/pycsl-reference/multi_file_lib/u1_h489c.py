from typing import List


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns \nothing
    def __len__(self) -> int:
        return 1


def k(o: C) -> int:
    return len(o)
