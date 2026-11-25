import zv83s2.b
import timeit

timeit.timeit("import zv83s2, zv83s2.c; zv83s2.b = zv83s2.c", number=1)


#@ ensures \result == 1
def g() -> int:
    return zv83s2.b.one()


print("result", g())
