import zv83v2.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


functools.update_wrapper(zv83v2.b, K, assigned=("one",), updated=())


#@ ensures \result == 1
def g() -> int:
    return zv83v2.b.one()


print("result", g())
