from zv75a4.k import three, Base


class D(Base):
    pass


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g() -> int:
    c = C()
    return c.b + three()


print("result", g())
