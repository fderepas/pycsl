import hw81x6
from dp81x6 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x6.one() + three()


print("result", g())
