from zv7xd7 import *
from zv7od7 import b


#@ ensures \result == 1
def g() -> int:
    return b()


print("result", g())
