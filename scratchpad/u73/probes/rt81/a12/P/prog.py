import zv81a12.b
from sw81a12 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a12.b.one()


swap()
print("result", g())
