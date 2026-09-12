from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self, d: Dict[int, int]) -> None:
        self.d = d


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    src = {1: 5}
    c = C(src)
    return c.d.get(1, 0)
