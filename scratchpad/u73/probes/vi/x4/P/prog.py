import hw81x4
from dp81x4 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x4.one() + three()


print("result", g())
