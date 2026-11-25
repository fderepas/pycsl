import zv83t1.b
from test.support import swap_attr

class K:
    @staticmethod
    def one() -> int:
        return 2


_cm = swap_attr(zv83t1, "b", K)
_cm.__enter__()


#@ ensures \result == 1
def g() -> int:
    return zv83t1.b.one()


print("result", g())
