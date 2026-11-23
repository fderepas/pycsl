import zv7g2


#@ ensures \result == 5
def g() -> int:
    return zv7g2.c.k()


print("result", g())
