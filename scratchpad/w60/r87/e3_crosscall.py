from typing import List


#@ requires xs[0] == 0
#@ ensures \result == 0
#@ assigns \nothing
def g(xs: List[int]) -> int:
    return 0


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return g(c.xs)
