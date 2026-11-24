import zv83o7.b
from hw83o7 import three


#@ ensures \result == 4
def g() -> int:
    return zv83o7.b.one() + three()


print("result", g())
