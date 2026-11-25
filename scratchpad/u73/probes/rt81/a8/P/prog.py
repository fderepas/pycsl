import zv81a8.b
from sw81a8 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a8.b.one()


swap()
print("result", g())
