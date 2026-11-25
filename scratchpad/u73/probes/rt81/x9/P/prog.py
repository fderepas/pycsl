import hw81x9
from dp81x9 import three


#@ ensures \result == 4
def g() -> int:
    return hw81x9.one() + three()


print("result", g())
