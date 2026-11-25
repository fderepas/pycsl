def run() -> None:
    import timeit
    timeit.timeit("import zu75c, zu75c.c; zu75c.b = zu75c.c", number=1)
