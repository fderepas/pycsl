import hn7
from depn7 import three


#@ ensures \result == 4
def g() -> int:
    return hn7.one() + three()


print("result", g())
