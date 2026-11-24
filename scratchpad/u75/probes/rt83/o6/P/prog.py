import zv83o6.b
from hw83o6 import three


#@ ensures \result == 4
def g() -> int:
    return zv83o6.b.one() + three()


print("result", g())
