from zw83q2 import *
import hw83q2


#@ ensures \result == 2
def g() -> int:
    return hw83q2.one() + 1


print("result", g())
