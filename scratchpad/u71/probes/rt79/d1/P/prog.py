import zv7d1
import ldd1


#@ ensures \result == 1
def g() -> int:
    return zv7d1.b()


print("result", g())
