from zun3 import *
from zun3.k import three


#@ ensures \result == 3
def g() -> int:
    return three()


print("result", g())
