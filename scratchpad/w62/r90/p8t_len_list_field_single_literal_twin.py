from typing import List
class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [4, 5, 6]

#@ ensures \result == 3
def f() -> int:
    c = C()
    return len(c.xs)
