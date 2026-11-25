import zv75e2.b
from hw75e2 import three


#@ ensures \result == 4
def g() -> int:
    return zv75e2.b.one() + three()


print("result", g())
