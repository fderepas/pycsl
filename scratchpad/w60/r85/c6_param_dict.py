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
    if 1 in c.d:
        return 1
    return 0
