import typing
import zv83f8.b

class K:
    @staticmethod
    def one() -> int:
        return 2


#@ assigns \nothing
def _sw() -> None:
    m = typing.ForwardRef("zv83f8", module="__main__").evaluate()
    setattr(m, "b", K)


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83f8.b.one()


print("result", g())
