import zv75c3.b
from zv75c3.b import one
import functools


def _two() -> int:
    return 2


functools.update_wrapper(one, _two, assigned=("__code__",), updated=())


#@ ensures \result == 1
def g() -> int:
    return zv75c3.b.one()


print("result", g())
