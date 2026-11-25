import zv81p2b.b


class C(zv81p2b):
    pass


#@ ensures \result == 1
def g() -> int:
    return zv81p2b.b.one()


print("result", g())
