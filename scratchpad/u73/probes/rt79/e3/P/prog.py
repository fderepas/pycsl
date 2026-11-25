import zv7e3.b


#@ ensures \result == 1
def g() -> int:
    return zv7e3.b.one()


print("result", g())
