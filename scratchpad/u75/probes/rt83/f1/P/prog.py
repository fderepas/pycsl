import typing
import zv83f1.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _sw() -> None:
    m = typing.ForwardRef("zv83f1", module="__main__").evaluate()
    m.b = K


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83f1.b.one()


print("result", g())
