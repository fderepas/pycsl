import zv7g1


#@ ensures \result == 6
def g() -> int:
    return zv7g1.c.k() + zv7g1.b()


print("result", g())
