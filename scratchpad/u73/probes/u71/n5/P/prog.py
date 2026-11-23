import hn5
from depn5 import three


#@ ensures \result == 4
def g() -> int:
    return hn5.one() + three()


print("result", g())
