import zv83c1f.b
from zv83c1f import Base


class C(Base):
    pass


#@ ensures \result == 1
def g() -> int:
    return zv83c1f.b.one()


print("result", g())
