from zv7xd9 import *
from zv7od9 import b


#@ ensures \result == 1
def g() -> int:
    return b()


print("result", g())
