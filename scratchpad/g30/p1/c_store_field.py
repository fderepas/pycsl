from typing import Optional


class Box:
    #@ assigns self.v
    #@ ensures self.v == 5
    def __init__(self) -> None:
        self.v: Optional[int] = 5


#@ ensures \result == 1
def probe() -> int:
    b = Box()
    b.v = None
    if b.v == 0:
        return 1
    return 2
