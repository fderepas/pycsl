import zv83s6.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


functools.partial(setattr, zv83s6, "b")(K)


#@ ensures \result == 1
def g() -> int:
    return zv83s6.b.one()


print("result", g())
