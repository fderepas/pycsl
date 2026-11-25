import zv83s0.b

exec("import zv83s0, zv83s0.c; zv83s0.b = zv83s0.c")


#@ ensures \result == 1
def g() -> int:
    return zv83s0.b.one()


print("result", g())
