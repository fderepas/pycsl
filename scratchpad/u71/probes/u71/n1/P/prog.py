import hn1
from depn1 import three


#@ ensures \result == 4
def g() -> int:
    return hn1.one() + three()


print("result", g())
