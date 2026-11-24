import zv75a3.k
from zv75a3.k import three


class D(zv75a3.k.Base):
    pass


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g() -> int:
    c = C()
    return c.b + three()


print("result", g())
