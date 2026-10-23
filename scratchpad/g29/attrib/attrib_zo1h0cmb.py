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


#@ ensures \result == 1
def probe(flag: int) -> int:
    if flag > 0:
        o = Alpha()
    else:
        o = Beta()
    return o.get()
