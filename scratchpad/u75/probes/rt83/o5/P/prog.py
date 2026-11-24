from typing import List
from zv83o5.k import three


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g(xs: List[int]) -> int:
    c = C()
    return c.b + three()


print("result", g([1]))
