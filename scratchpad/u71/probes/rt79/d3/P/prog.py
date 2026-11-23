import zv7d3
import ldd3


#@ ensures \result == 1
def g() -> int:
    return zv7d3.b()


print("result", g())
