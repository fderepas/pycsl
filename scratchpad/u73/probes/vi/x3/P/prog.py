import hw81x3
from dp81x3 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x3.one() + three()


print("result", g())
