from zv83h7 import *
import hw83h7


#@ ensures \result == 2
def g() -> int:
    return hw83h7.one() + 1


print("result", g())
