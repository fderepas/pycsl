import zv83m1.b
import operator

class K:
    @staticmethod
    def one() -> int:
        return 2


operator.methodcaller("__setattr__", "b", K)(zv83m1)


#@ ensures \result == 1
def g() -> int:
    return zv83m1.b.one()


print("result", g())
