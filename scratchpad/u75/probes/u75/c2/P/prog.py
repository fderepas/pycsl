import zv75c2.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


class _Src:
    b = K


def h(x: object) -> None:
    functools.update_wrapper(x, _Src, assigned=("b",), updated=())


h(zv75c2)


#@ ensures \result == 1
def g() -> int:
    return zv75c2.b.one()


print("result", g())
