from typing import Optional


class C:
    o: Optional[int]

    #@ assigns self.o
    def __init__(self) -> None:
        self.o = 5


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    if c.o is None:
        return 1
    return 0
