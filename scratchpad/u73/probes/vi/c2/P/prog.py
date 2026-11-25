from zv83c2 import *
import hw83c2


#@ ensures \result == 1
def g() -> int:
    return hw83c2.one()


print("result", g())
