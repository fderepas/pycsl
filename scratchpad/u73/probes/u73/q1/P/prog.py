from zw83q1 import *
import hw83q1


#@ ensures \result == 2
def g() -> int:
    return hw83q1.one() + 1


print("result", g())
