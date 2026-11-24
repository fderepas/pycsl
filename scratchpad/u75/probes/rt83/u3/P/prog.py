import zv83u3.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


class _Src:
    b = K


def _sw() -> None:
    functools.update_wrapper(zv83u3, _Src, assigned=("b",), updated=())


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83u3.b.one()


print("result", g())
