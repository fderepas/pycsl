from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self, xs: List[int]) -> None:
        self.xs = xs


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    src = [1, 2, 3]
    c = C(src)
    return c.xs[0]
