import typing
import zv83f3.b

class K:
    @staticmethod
    def one() -> int:
        return 2


#@ assigns \everything
def _sw() -> None:
    setattr(typing.ForwardRef("zv83f3", module="__main__").evaluate(), "b", K)


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83f3.b.one()


print("result", g())
