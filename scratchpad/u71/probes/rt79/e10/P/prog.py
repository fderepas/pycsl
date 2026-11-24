import zv7e10.b
from swe10 import swap


#@ ensures \result == 1
def g() -> int:
    return zv7e10.b.one()


swap()
print("result", g())
