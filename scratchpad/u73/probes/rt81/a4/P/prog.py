import zv81a4.b
from sw81a4 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a4.b.one()


swap()
print("result", g())
