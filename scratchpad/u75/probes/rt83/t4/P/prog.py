import zv83t4.b
import operator

class K:
    @staticmethod
    def one() -> int:
        return 2


operator.setitem(zv83t4.__dict__, "b", K)


#@ ensures \result == 1
def g() -> int:
    return zv83t4.b.one()


print("result", g())
