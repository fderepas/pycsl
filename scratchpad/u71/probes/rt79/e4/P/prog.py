import zv7e4.b


#@ ensures \result == 1
def g() -> int:
    return zv7e4.b.one()


print("result", g())
