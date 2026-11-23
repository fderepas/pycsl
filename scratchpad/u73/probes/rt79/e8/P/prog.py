import zv7e8.b


#@ ensures \result == 1
def g() -> int:
    return zv7e8.b.one()


print("result", g())
