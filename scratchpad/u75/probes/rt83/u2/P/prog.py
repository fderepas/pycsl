import zv83u2.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


class _Src:
    b = K


functools.wraps(_Src, assigned=(), updated=("__dict__",))(zv83u2)


#@ ensures \result == 1
def g() -> int:
    return zv83u2.b.one()


print("result", g())
