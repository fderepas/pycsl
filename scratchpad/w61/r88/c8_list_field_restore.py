from typing import List
class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [0, 0, 0, 0]
        self.xs = [0, 0]

#@ ensures \result == 4
def f() -> int:
    c = C()
    return len(c.xs)
