from typing import List
class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self, k: int) -> None:
        self.xs = []
        if k > 0:
            self.xs = [7, 8]

#@ ensures \result == 0
def f() -> int:
    c = C(1)
    return len(c.xs)
