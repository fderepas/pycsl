import zv7d5
from ldd5 import h


#@ ensures \result == 1
def g() -> int:
    return zv7d5.b()


h()
print("result", g())
