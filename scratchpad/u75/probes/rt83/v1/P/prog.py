import zv83v1.b


def _two() -> int:
    return 2


def _sw() -> None:
    m = zv83v1.__getattribute__("b")
    m.one = _two


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83v1.b.one()


print("result", g())
