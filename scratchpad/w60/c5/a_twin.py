from typing import Dict


def g(d: Dict[int, int]) -> int:
    if 1 in d:
        return 1
    return 0


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
    return g(c.d)
