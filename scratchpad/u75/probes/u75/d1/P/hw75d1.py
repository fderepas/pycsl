def run() -> None:
    import timeit
    timeit.timeit("import zv75d1, zv75d1.c; zv75d1.b = zv75d1.c", number=1)
