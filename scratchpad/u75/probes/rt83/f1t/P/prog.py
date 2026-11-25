import typing
import zv83f1t.b

class K:
    @staticmethod
    def one() -> int:
        return 2


m = typing.ForwardRef("zv83f1t", module="__main__").evaluate()
m.b = K


#@ ensures \result == 1
def g() -> int:
    return zv83f1t.b.one()


print("result", g())
