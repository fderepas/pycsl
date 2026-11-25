import zv81a2.b
from sw81a2 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a2.b.one()


swap()
print("result", g())
