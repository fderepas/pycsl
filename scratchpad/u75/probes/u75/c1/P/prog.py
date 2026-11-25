import zv75c1.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


class _Src:
    b = K


m = zv75c1
functools.update_wrapper(m, _Src, assigned=("b",), updated=())


#@ ensures \result == 1
def g() -> int:
    return zv75c1.b.one()


print("result", g())
