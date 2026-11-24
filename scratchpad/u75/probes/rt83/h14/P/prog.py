import zv83h14.b


#@ ensures \result == 1
def g() -> int:
    return zv83h14.b.one()


print("result", g())
