import pickle
import zv83o2.b


#@ ensures \result == 1
def g() -> int:
    return zv83o2.b.one()


print("result", g())
