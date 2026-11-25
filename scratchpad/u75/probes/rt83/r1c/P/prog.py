import zv83r1c


#@ ensures \result == 1
def g() -> int:
    return zv83r1c.b.one()


print("result", g())
