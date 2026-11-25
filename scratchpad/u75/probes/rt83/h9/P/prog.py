from zv83h9 import *
import hw83h9


#@ ensures \result == 2
def g() -> int:
    return hw83h9.one() + 1


print("result", g())
