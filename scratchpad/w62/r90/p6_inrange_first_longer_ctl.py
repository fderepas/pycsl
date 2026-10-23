from typing import List
class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]
        self.xs = [7, 8]

#@ ensures \result == 8
def f() -> int:
    c = C()
    return c.xs[1]
