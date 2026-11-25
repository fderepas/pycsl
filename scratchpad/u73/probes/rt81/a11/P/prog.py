import zv81a11.b
from sw81a11 import swap


#@ ensures \result == 1
def g() -> int:
    return zv81a11.b.one()


swap()
print("result", g())
