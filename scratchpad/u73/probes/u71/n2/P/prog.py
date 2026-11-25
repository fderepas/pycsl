import hn2
from depn2 import three


#@ ensures \result == 4
def g() -> int:
    return hn2.one() + three()


print("result", g())
