import hw81x1
from dp81x1 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x1.one() + three()


print("result", g())
