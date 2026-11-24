from zv83h6 import *
import hw83h6


#@ ensures \result == 2
def g() -> int:
    return hw83h6.one() + 1


print("result", g())
