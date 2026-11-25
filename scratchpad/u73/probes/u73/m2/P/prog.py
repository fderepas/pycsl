import zv83m2.b


class C(zv83m2):
    pass


#@ ensures \result == 1
def g() -> int:
    return zv83m2.b.one()


print("result", g())
