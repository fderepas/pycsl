import hw81x2
from dp81x2 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x2.one() + three()


print("result", g())
