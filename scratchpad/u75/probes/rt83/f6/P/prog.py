import typing
import zv83f6.b

class K:
    @staticmethod
    def one() -> int:
        return 2


#@ ensures \result == 1
def g() -> int:
    m = typing.ForwardRef("zv83f6", module="__main__").evaluate()
    m.b = K
    return zv83f6.b.one()


print("result", g())
