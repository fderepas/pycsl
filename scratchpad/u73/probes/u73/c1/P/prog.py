import zv83c1.b


class C(zv83c1.Base):
    pass


#@ ensures \result == 1
def g() -> int:
    return zv83c1.b.one()


print("result", g())
