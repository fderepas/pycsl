from typing import List


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __eq__(self, x: object) -> bool:
        self.v = 7
        return True


def k(o: C) -> int:
    return 1 if o == 1 else 0
