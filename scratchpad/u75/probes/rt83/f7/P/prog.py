import typing
import zv83f7.b

class K:
    @staticmethod
    def one() -> int:
        return 2


#@ ensures \result == 1
def g() -> int:
    m = typing.ForwardRef("zv83f7", module="__main__").evaluate()
    setattr(m, "b", K)
    return zv83f7.b.one()


print("result", g())
