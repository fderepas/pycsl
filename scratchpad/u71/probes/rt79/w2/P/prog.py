import hw792
from depw792 import three


#@ ensures \result == 4
def g() -> int:
    return hw792.one() + three()


print("result", g())
