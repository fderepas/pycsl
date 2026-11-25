import hw83m1
import zv83m1


class C(zv83m1):
    pass


#@ ensures \result == 1
def g() -> int:
    return hw83m1.one()


print("result", g())
