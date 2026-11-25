import typing
import zv83f5.b

class K:
    @staticmethod
    def one() -> int:
        return 2


class _S:
    def go(self) -> None:
        setattr(typing.ForwardRef("zv83f5", module="__main__").evaluate(), "b", K)


_S().go()


#@ ensures \result == 1
def g() -> int:
    return zv83f5.b.one()


print("result", g())
