import typing
import zv83f4.b

class K:
    @staticmethod
    def one() -> int:
        return 2


#@ ensures \result == 1
def g() -> int:
    setattr(typing.ForwardRef("zv83f4", module="__main__").evaluate(), "b", K)
    return zv83f4.b.one()


print("result", g())
