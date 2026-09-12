from typing import Set


class C:
    s: Set[int]

    #@ assigns self.s
    def __init__(self) -> None:
        self.s = {7}


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    if 7 in c.s:
        return 1
    return 0
