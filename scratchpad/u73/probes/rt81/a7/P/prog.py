import zv81a7.b
from sw81a7 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a7.b.one()


swap()
print("result", g())
