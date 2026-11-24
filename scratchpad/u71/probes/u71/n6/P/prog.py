import hn6
from depn6 import three


#@ ensures \result == 4
def g() -> int:
    return hn6.one() + three()


print("result", g())
