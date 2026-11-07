from typing import List
class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2]
        self.xs = [3, 4, 5]

#@ ensures \result == 2
def f() -> int:
    c = C()
    return len(c.xs)
