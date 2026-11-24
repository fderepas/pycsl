import zv7e5.b


#@ ensures \result == 1
def g() -> int:
    return zv7e5.b.one()


print("result", g())
