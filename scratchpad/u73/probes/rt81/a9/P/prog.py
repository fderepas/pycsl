import zv81a9.b
from sw81a9 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a9.b.one()


swap()
print("result", g())
