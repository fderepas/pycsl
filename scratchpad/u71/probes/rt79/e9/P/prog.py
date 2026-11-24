import zv7e9.b
from swe9 import swap


#@ ensures \result == 1
def g() -> int:
    return zv7e9.b.one()


swap()
print("result", g())
