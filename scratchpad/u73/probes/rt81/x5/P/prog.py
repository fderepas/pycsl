import hw81x5
from dp81x5 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x5.one() + three()


print("result", g())
