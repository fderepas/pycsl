from typing import Dict

from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    if 1 in c.d:
        return 1
    return 0


