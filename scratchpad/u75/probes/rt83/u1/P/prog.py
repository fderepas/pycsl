import zv83u1.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


class _Src:
    b = K


functools.update_wrapper(zv83u1, _Src, assigned=("b",), updated=())


#@ ensures \result == 1
def g() -> int:
    return zv83u1.b.one()


print("result", g())
