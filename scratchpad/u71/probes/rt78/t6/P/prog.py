import zt786.b
import zt786.c
zt786.b = zt786.c


#@ ensures \result == 1
def g() -> int:
    return zt786.b.one()


print("result", g())
