from zv83h8 import *
import hw83h8


#@ ensures \result == 2
def g() -> int:
    return hw83h8.one() + 1


print("result", g())
