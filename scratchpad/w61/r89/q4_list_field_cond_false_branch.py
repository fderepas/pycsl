from typing import List
class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self, k: int) -> None:
        self.xs = [1, 2]
        if k > 0:
            self.xs = [7, 8]

#@ ensures \result == 7
def f() -> int:
    c = C(0)
    return c.xs[0]
