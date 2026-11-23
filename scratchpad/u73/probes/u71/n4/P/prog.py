import hn4
from zun4.k import three


#@ ensures \result == 4
def g() -> int:
    return hn4.one() + three()


print("result", g())
