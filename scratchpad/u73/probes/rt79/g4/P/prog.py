from zv7g4 import c


#@ ensures \result == 5
def g() -> int:
    return c.k()


print("result", g())
