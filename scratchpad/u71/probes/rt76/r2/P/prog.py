import zr76.b


#@ ensures \result == 1
def g() -> int:
    return zr76.b.one()


print("result", g())
