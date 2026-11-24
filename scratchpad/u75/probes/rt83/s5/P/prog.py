import zv83s5.b
from hw83s5 import three


#@ ensures \result == 4
def g() -> int:
    return zv83s5.b.one() + three()


print("result", g())
