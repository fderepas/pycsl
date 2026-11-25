import zv7e1.b


#@ ensures \result == 1
def g() -> int:
    return zv7e1.b.one()


print("result", g())
