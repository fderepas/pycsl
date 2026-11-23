import zv7e2.b


#@ ensures \result == 1
def g() -> int:
    return zv7e2.b.one()


print("result", g())
