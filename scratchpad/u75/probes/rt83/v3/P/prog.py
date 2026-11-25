import zv83v3.b
from test.support import swap_attr


def _two() -> int:
    return 2


_cm = swap_attr(zv83v3.b, "one", _two)
_cm.__enter__()


#@ ensures \result == 1
def g() -> int:
    return zv83v3.b.one()


print("result", g())
