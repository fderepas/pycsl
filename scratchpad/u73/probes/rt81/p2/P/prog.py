import zv81p2.b


class C(zv81p2):
    pass


#@ ensures \result == 1
def g() -> int:
    return zv81p2.b.one()


print("result", g())
