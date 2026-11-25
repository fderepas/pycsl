import zv81a1.b
from sw81a1 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a1.b.one()


swap()
print("result", g())
