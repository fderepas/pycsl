import hw81x8
from dp81x8 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x8.one() + three()


print("result", g())
