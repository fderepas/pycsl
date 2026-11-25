import typing
from zv75a2.k import three


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g(xs: typing.List[int]) -> int:
    c = C()
    return c.b + three()


print("result", g([1]))
