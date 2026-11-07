from typing import List
class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2]
        self.xs = [3, 4, 5]

#@ ensures \result == 1
def f() -> int:
    c = C()
    return c.xs[0]
