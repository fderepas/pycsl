from zv7xd8 import *
import zv7od8


#@ ensures \result == 1
def g() -> int:
    return zv7od8.b()


print("result", g())
