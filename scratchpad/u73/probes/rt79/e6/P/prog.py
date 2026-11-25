import zv7e6.b


#@ ensures \result == 1
def g() -> int:
    return zv7e6.b.one()


print("result", g())
