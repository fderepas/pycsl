from zv75a5.k import three, Base


class D(Base):
    pass


_G = globals()

class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g() -> int:
    c = C()
    return c.b + three()


print("result", g())
