import zv81a5.b
from sw81a5 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a5.b.one()


swap()
print("result", g())
