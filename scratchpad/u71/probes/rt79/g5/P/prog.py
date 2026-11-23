from zv7g5.c import k
from zv7g5 import c


#@ ensures \result == 5
def g() -> int:
    return c.k()


print("result", g())
