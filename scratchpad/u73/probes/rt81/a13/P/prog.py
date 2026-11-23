import zv81a13.b
from sw81a13 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a13.b.one()


swap()
print("result", g())
