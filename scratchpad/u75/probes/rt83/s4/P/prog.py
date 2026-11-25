import zv83s4.b
import timeit


def _sw() -> None:
    timeit.timeit("import zv83s4, zv83s4.c; zv83s4.b = zv83s4.c", number=1)


_sw()


#@ ensures \result == 1
def g() -> int:
    return zv83s4.b.one()


print("result", g())
