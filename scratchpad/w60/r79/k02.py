from typing import List


class C:
    n: int

    #@ assigns self.n
    def __init__(self, items: List[int]) -> None:
        self.n = len(items)


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C([1, 2, 3])
    return c.n
