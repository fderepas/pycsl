import zv7e7.b


#@ ensures \result == 1
def g() -> int:
    return zv7e7.b.one()


print("result", g())
