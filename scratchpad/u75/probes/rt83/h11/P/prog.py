import zv83h11.b
zv83h11()


#@ ensures \result == 1
def g() -> int:
    return zv83h11.b.one()


print("result", g())
