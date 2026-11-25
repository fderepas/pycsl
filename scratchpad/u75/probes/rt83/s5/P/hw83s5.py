import timeit


#@ ensures \result == 3
def three() -> int:
    return 3


timeit.timeit("import zv83s5, zv83s5.c; zv83s5.b = zv83s5.c", number=1)
