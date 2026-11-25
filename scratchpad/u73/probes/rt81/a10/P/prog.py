import zv81a10.b
from sw81a10 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a10.b.one()


swap()
print("result", g())
