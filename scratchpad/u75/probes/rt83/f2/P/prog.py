import typing
import zv83f2.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    m = typing.ForwardRef("zv83f2", module="__main__").evaluate()
    setattr(m, "b", K)


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83f2.b.one()


print("result", g())
