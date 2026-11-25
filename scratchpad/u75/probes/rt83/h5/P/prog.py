from zv83h5 import *
import hw83h5


#@ ensures \result == 2
def g() -> int:
    return hw83h5.one() + 1


print("result", g())
