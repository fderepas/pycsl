import zv83h2.b


#@ ensures \result == 1
def g() -> int:
    return zv83h2.b.one()


print("result", g())
