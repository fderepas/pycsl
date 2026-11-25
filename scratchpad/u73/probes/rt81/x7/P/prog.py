import hw81x7
from dp81x7 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x7.one() + three()


print("result", g())
