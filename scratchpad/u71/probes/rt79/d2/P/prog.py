import zv7d2
import ldd2


#@ ensures \result == 1
def g() -> int:
    return zv7d2.b()


print("result", g())
