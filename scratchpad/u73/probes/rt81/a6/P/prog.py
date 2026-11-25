import zv81a6.b
from sw81a6 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a6.b.one()


swap()
print("result", g())
