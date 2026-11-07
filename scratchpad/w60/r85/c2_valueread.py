from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.d.get(1, 0)
