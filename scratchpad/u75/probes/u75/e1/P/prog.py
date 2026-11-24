import zv75e1.b
from hw75e1 import three


#@ ensures \result == 4
def g() -> int:
    return zv75e1.b.one() + three()


print("result", g())
